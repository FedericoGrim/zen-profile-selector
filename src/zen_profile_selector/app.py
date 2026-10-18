from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from collections.abc import Callable
from dataclasses import replace
from datetime import date
from functools import partial
from pathlib import Path
from tkinter import filedialog
from typing import TypeVar

import customtkinter as ctk
from send2trash import send2trash

from .config import Settings, config_dir, load_settings, save_settings, validate_settings, xdg_config_home
from .desktop import desktop_file, install_desktop_entry, uninstall_desktop_entry
from .i18n import LANGUAGES, detect_language, translate
from .layout import grid_columns, primary_monitor
from .profiles import (
    DEFAULT_ICON,
    ICON_CHOICES,
    icon_for,
    load_icons,
    profile_in_use,
    read_profiles,
    remove_icon,
    remove_profile,
    rename_icon,
    rename_profile,
    save_icon,
    validate_profile_name,
)
from .version import (
    UPGRADE_COMMAND,
    fetch_latest_version,
    installed_version,
    load_update_state,
    pipx_upgrade_command,
    save_update_state,
    update_check_due,
    version_to_announce,
)
from .zen import ZenInstall, create_profile_command, detect_zen, launch_command

ASSETS = Path(__file__).with_name("assets")
T = TypeVar("T")
ICONS_FILE_NAME = "profile_icons.json"

BACKGROUND = "#212122"
CARD = "#2a2a2a"
CARD_BORDER = "#333333"
HOVER = "#3a3a3a"
TEXT = "#e8e8e8"
ERROR = "#ff6464"


class ProfileSelector:
    def __init__(self, root: ctk.CTk, settings_dir: Path):
        self.root = root
        self.settings_dir = settings_dir
        self.icons_file = settings_dir / ICONS_FILE_NAME
        self.settings = load_settings(settings_dir)
        self.language = self.settings.language or detect_language(os.environ)
        self.install: ZenInstall | None = None
        self.profiles: dict[str, str] = {}
        self.version = installed_version()
        self.update_state = load_update_state(settings_dir)

        ctk.set_appearance_mode("dark")
        self.root.title("Zen Profile Selector")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BACKGROUND)
        self.logo = tk.PhotoImage(file=ASSETS / "icon-header.png")
        self.root.iconphoto(True, self.logo)

        self.build()
        self.start_update_check()

    def text(self, key: str, **values: str) -> str:
        return translate(self.language, key, **values)

    def change_language(self, language_name: str) -> None:
        self.language = next(code for code, name in LANGUAGES.items() if name == language_name)
        self.settings = replace(self.settings, language=self.language)
        save_settings(self.settings_dir, self.settings)
        self.build()

    def build_top_bar(self) -> None:
        bar = ctk.CTkFrame(self.root, fg_color=BACKGROUND)
        bar.pack(fill="x", padx=12, pady=(12, 0))
        language_menu = ctk.CTkOptionMenu(
            bar,
            values=list(LANGUAGES.values()),
            command=self.change_language,
            width=110,
            height=28,
            fg_color=CARD,
            button_color=CARD,
            button_hover_color=HOVER,
            dropdown_fg_color=CARD,
            dropdown_hover_color=HOVER,
            text_color=TEXT,
        )
        language_menu.set(LANGUAGES[self.language])
        ctk.CTkButton(
            bar,
            text="⚙",
            font=("Arial", 16),
            width=28,
            height=28,
            fg_color=CARD,
            hover_color=HOVER,
            text_color=TEXT,
            command=self.open_settings_dialog,
        ).pack(side="right")
        language_menu.pack(side="right", padx=(0, 6))

    def build_update_banner(self) -> None:
        """Small banner with the upgrade command when a newer version is on PyPI."""
        version = version_to_announce(self.update_state, self.version)
        if version is None:
            return
        banner = ctk.CTkFrame(self.root, fg_color=CARD, corner_radius=8)
        banner.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkButton(
            banner,
            text="✕",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=HOVER,
            text_color=TEXT,
            command=partial(self.dismiss_update, version),
        ).pack(side="right", padx=(0, 6))
        message = ctk.CTkLabel(
            banner,
            text=self.text("update_available", version=version, command=UPGRADE_COMMAND),
            text_color=TEXT,
            justify="left",
            anchor="w",
        )
        action = ctk.CTkButton(banner, width=110, height=28, fg_color=HOVER, hover_color="#4a4a4a")
        upgrade = pipx_upgrade_command(sys.executable)
        if upgrade:
            message.configure(text=self.text("update_ready", version=version))
            action.configure(
                text=self.text("update"), command=partial(self.run_upgrade, upgrade, version, message, action)
            )
        else:
            action.configure(
                text=self.text("copy_command"), command=partial(self.copy_upgrade_command, action)
            )
        action.pack(side="right", padx=6)
        message.pack(side="left", fill="x", expand=True, padx=12, pady=8)

    def copy_upgrade_command(self, button: ctk.CTkButton) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(UPGRADE_COMMAND)
        button.configure(text=self.text("copied"))

    def run_upgrade(
        self, command: list[str], version: str, message: ctk.CTkLabel, button: ctk.CTkButton
    ) -> None:
        """Upgrade with pipx in the background, then offer a restart; on failure show the manual command."""
        button.configure(text=self.text("updating"), state="disabled")

        def upgrade() -> bool:
            try:
                return subprocess.run(command, capture_output=True, timeout=300).returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                return False

        def done(succeeded: bool) -> None:
            if succeeded:
                message.configure(text=self.text("update_done", version=version))
                button.configure(text=self.text("restart"), state="normal", command=self.restart)
            else:
                message.configure(text=self.text("update_failed", command=UPGRADE_COMMAND))
                button.configure(
                    text=self.text("copy_command"),
                    state="normal",
                    command=partial(self.copy_upgrade_command, button),
                )

        self.run_in_background(upgrade, done)

    def restart(self) -> None:
        command = [sys.executable, "-m", "zen_profile_selector"]
        if sys.platform == "win32":
            # os.execv on Windows starts a new process and returns, leaving both windows open
            subprocess.Popen(command)
            self.root.quit()
        else:
            os.execv(sys.executable, command)

    def run_in_background(self, work: Callable[[], T], on_done: Callable[[T], None]) -> None:
        """Run work in a thread and hand its result to on_done in the Tk main loop."""
        result: list[T] = []
        thread = threading.Thread(target=lambda: result.append(work()), daemon=True)
        thread.start()

        def poll() -> None:
            # Tk is not thread safe: poll from the main loop instead of calling it from the thread
            if thread.is_alive():
                self.root.after(200, poll)
            elif result:
                on_done(result[0])

        self.root.after(200, poll)

    def dismiss_update(self, version: str) -> None:
        self.update_state = replace(self.update_state, dismissed=version)
        save_update_state(self.settings_dir, self.update_state)
        self.build()

    def start_update_check(self) -> None:
        """Ask PyPI for the latest version in the background, at most once a day."""
        if not (
            self.settings.check_updates and self.version and update_check_due(self.update_state, date.today())
        ):
            return

        def finish(latest: str | None) -> None:
            if not latest:
                return  # offline: try again at the next start
            announced = version_to_announce(self.update_state, self.version)
            self.update_state = replace(self.update_state, checked=date.today().isoformat(), latest=latest)
            save_update_state(self.settings_dir, self.update_state)
            if version_to_announce(self.update_state, self.version) != announced:
                self.build()

        self.run_in_background(fetch_latest_version, finish)

    def detect(self, settings: Settings) -> ZenInstall | None:
        return detect_zen(
            Path.home(),
            command=settings.zen_command or None,
            profiles_dir=settings.profiles_dir_path,
            config_home=xdg_config_home(os.environ, Path.home()),
        )

    def build(self) -> None:
        """Create (or recreate) the logo and the profile grid."""
        for widget in self.root.winfo_children():
            if not isinstance(widget, ctk.CTkToplevel):
                widget.destroy()

        self.install = self.detect(self.settings)
        self.profiles = read_profiles(self.install.profiles_dir) if self.install else {}

        self.build_top_bar()
        self.build_update_banner()
        tk.Label(self.root, image=self.logo, bg=BACKGROUND, borderwidth=0, highlightthickness=0).pack(
            pady=(0, 20), padx=20
        )

        if self.install is None:
            ctk.CTkLabel(self.root, text=self.text("zen_not_found"), text_color=ERROR).pack(
                padx=40, pady=(0, 40)
            )
            self.fit_window_to_content()
            return

        icons = load_icons(self.icons_file)
        grid = ctk.CTkFrame(self.root, fg_color=BACKGROUND)
        grid.pack(pady=(0, 40), padx=40, fill="both", expand=True)

        columns = grid_columns(len(self.profiles) + 1)
        for index, (name, path) in enumerate(self.profiles.items()):
            row, column = divmod(index, columns)
            self.create_card(
                grid,
                icon_for(icons, name),
                name,
                partial(self.launch_zen, path),
                row,
                column,
                on_edit=partial(self.open_edit_profile_dialog, name),
            )
        row, column = divmod(len(self.profiles), columns)
        self.create_card(grid, "＋", self.text("new_card"), self.open_new_profile_dialog, row, column)

        self.fit_window_to_content()

    def fit_window_to_content(self) -> None:
        """Size the window to its content and center it on the primary monitor."""
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        monitor_x, monitor_y, monitor_width, monitor_height = self.screen_area()
        x = monitor_x + (monitor_width - width) // 2
        y = monitor_y + (monitor_height - height) // 2
        # CustomTkinter rescales width and height, not the position
        scaling = ctk.ScalingTracker.get_window_scaling(self.root)
        self.root.geometry(f"{round(width / scaling)}x{round(height / scaling)}+{x}+{y}")

    def screen_area(self) -> tuple[int, int, int, int]:
        """Primary monitor; the whole screen without xrandr (e.g. native Wayland)."""
        try:
            output = subprocess.run(
                ["xrandr", "--listmonitors"], capture_output=True, text=True, timeout=2
            ).stdout
        except (OSError, subprocess.TimeoutExpired):
            output = ""
        return primary_monitor(output) or (
            0,
            0,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
        )

    def create_card(
        self,
        parent: ctk.CTkFrame,
        icon: str,
        label: str,
        command: Callable[[], None],
        row: int,
        column: int,
        on_edit: Callable[[], None] | None = None,
    ) -> None:
        """Square card with an icon and a name; with on_edit it shows ✎ on hover."""
        card = ctk.CTkButton(
            parent,
            text="",
            fg_color=CARD,
            hover_color=HOVER,
            border_width=1,
            border_color=CARD_BORDER,
            width=140,
            height=140,
            corner_radius=8,
            command=command,
        )
        card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        icon_label = ctk.CTkLabel(content, text=icon, font=("Arial", 40))
        icon_label.pack(pady=(10, 5))
        name_label = ctk.CTkLabel(content, text=label, font=("Arial", 13, "bold"), text_color=TEXT)
        name_label.pack()

        # Icon and name sit on top of the button: forward clicks and hover to the card
        for widget in (content, icon_label, name_label):
            widget.bind("<ButtonRelease-1>", lambda event: command())
            widget.bind("<Enter>", lambda event: card._on_enter())

        if on_edit is None:
            return

        edit_button = ctk.CTkButton(
            card,
            text="✎",
            font=("Arial", 14),
            width=26,
            height=26,
            fg_color=HOVER,
            bg_color=HOVER,
            hover_color="#4a4a4a",
            text_color=TEXT,
            corner_radius=6,
            command=on_edit,
        )

        def show_edit(event: tk.Event | None = None) -> None:
            edit_button.place(relx=1, x=-6, y=6, anchor="ne")

        def hide_edit_if_outside() -> None:
            # Leave also fires over the inner labels: hide only once the pointer has left the card
            pointer = card.winfo_containing(*card.winfo_pointerxy())
            if not pointer or not str(pointer).startswith(str(card)):
                edit_button.place_forget()

        for widget in (card, content, icon_label, name_label):
            widget.bind("<Enter>", show_edit, add="+")
            widget.bind("<Leave>", lambda event: card.after(50, hide_edit_if_outside), add="+")

    def open_dialog(self, title: str) -> ctk.CTkToplevel:
        dialog = ctk.CTkToplevel(self.root, fg_color=BACKGROUND)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.geometry(f"+{self.root.winfo_rootx() + 40}+{self.root.winfo_rooty() + 40}")
        dialog.after(100, dialog.grab_set)
        return dialog

    def open_profile_dialog(
        self,
        title: str,
        confirm_text: str,
        on_confirm: Callable[[str, str], str | None],
        name: str = "",
        icon: str = DEFAULT_ICON,
        on_delete: Callable[[ctk.CTkToplevel], None] | None = None,
    ) -> None:
        """Name and icon form; on_confirm(name, icon) returns an error key or None."""
        dialog = self.open_dialog(title)

        name_entry = ctk.CTkEntry(dialog, placeholder_text=self.text("profile_name"), width=320)
        name_entry.insert(0, name)
        name_entry.pack(padx=24, pady=(24, 16))

        selected_icon = tk.StringVar(value=icon)
        icons_frame = ctk.CTkFrame(dialog, fg_color=BACKGROUND)
        icons_frame.pack(padx=24)
        icon_buttons: dict[str, ctk.CTkButton] = {}

        def select_icon(choice: str) -> None:
            selected_icon.set(choice)
            for option, button in icon_buttons.items():
                button.configure(border_color=TEXT if option == choice else CARD_BORDER)

        choices = ICON_CHOICES if icon in ICON_CHOICES else [*ICON_CHOICES, icon]
        for index, choice in enumerate(choices):
            button = ctk.CTkButton(
                icons_frame,
                text=choice,
                font=("Arial", 22),
                width=44,
                height=44,
                fg_color=CARD,
                hover_color=HOVER,
                border_width=2,
                corner_radius=8,
                command=lambda choice=choice: select_icon(choice),
            )
            button.grid(row=index // 6, column=index % 6, padx=4, pady=4)
            icon_buttons[choice] = button
        select_icon(icon)

        error_label = ctk.CTkLabel(dialog, text="", text_color=ERROR)
        error_label.pack(padx=24, pady=(8, 0))

        def confirm() -> None:
            error = on_confirm(name_entry.get().strip(), selected_icon.get())
            if error:
                error_label.configure(text=self.text(error))
                return
            dialog.destroy()
            self.build()

        buttons = ctk.CTkFrame(dialog, fg_color=BACKGROUND)
        buttons.pack(padx=24, pady=(8, 24 if on_delete is None else 8), fill="x")
        ctk.CTkButton(
            buttons, text=self.text("cancel"), fg_color=CARD, hover_color=HOVER, command=dialog.destroy
        ).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(buttons, text=confirm_text, command=confirm).pack(side="left", expand=True, padx=(4, 0))

        if on_delete is not None:
            ctk.CTkButton(
                dialog,
                text=self.text("delete_profile_button"),
                fg_color="transparent",
                hover_color="#3a2222",
                text_color=ERROR,
                command=lambda: on_delete(dialog),
            ).pack(padx=24, pady=(0, 16))

        name_entry.bind("<Return>", lambda event: confirm())
        dialog.after(100, name_entry.focus_set)

    def open_settings_dialog(self) -> None:
        """Manual Zen command and profiles folder; empty fields mean detect automatically."""
        dialog = self.open_dialog(self.text("settings_title"))
        detected = self.detect(Settings())

        def field(label_key: str, value: str, placeholder: str) -> ctk.CTkEntry:
            ctk.CTkLabel(dialog, text=self.text(label_key), text_color=TEXT, anchor="w").pack(
                fill="x", padx=24, pady=(16, 4)
            )
            row = ctk.CTkFrame(dialog, fg_color=BACKGROUND)
            row.pack(fill="x", padx=24)
            entry = ctk.CTkEntry(row, placeholder_text=placeholder, width=360)
            if value:
                entry.insert(0, value)
            entry.pack(side="left")
            return entry

        command_entry = field(
            "zen_command_label", self.settings.zen_command, " ".join(detected.command) if detected else ""
        )
        profiles_entry = field(
            "profiles_dir_label", self.settings.profiles_dir, str(detected.profiles_dir) if detected else ""
        )

        def browse() -> None:
            folder = filedialog.askdirectory(parent=dialog)
            if folder:
                profiles_entry.delete(0, "end")
                profiles_entry.insert(0, folder)

        ctk.CTkButton(
            profiles_entry.master,
            text=self.text("browse"),
            width=90,
            fg_color=CARD,
            hover_color=HOVER,
            command=browse,
        ).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(dialog, text=self.text("settings_hint"), text_color="#9a9a9a", anchor="w").pack(
            fill="x", padx=24, pady=(8, 0)
        )

        def detect_automatically() -> None:
            for entry in (command_entry, profiles_entry):
                entry.delete(0, "end")
            dialog.focus_set()

        ctk.CTkButton(
            dialog,
            text=self.text("auto_detect"),
            fg_color="transparent",
            hover_color=HOVER,
            text_color=TEXT,
            command=detect_automatically,
        ).pack(anchor="w", padx=18, pady=(4, 0))

        check_updates = tk.BooleanVar(value=self.settings.check_updates)
        ctk.CTkCheckBox(
            dialog, text=self.text("check_updates"), variable=check_updates, text_color=TEXT
        ).pack(anchor="w", padx=24, pady=(12, 0))

        error_label = ctk.CTkLabel(dialog, text="", text_color=ERROR)
        error_label.pack(padx=24, pady=(8, 0))

        def save() -> None:
            command, profiles_dir = command_entry.get().strip(), profiles_entry.get().strip()
            error = validate_settings(command, profiles_dir)
            if error:
                error_label.configure(text=self.text(error))
                return
            self.settings = replace(
                self.settings,
                zen_command=command,
                profiles_dir=profiles_dir,
                check_updates=check_updates.get(),
            )
            save_settings(self.settings_dir, self.settings)
            dialog.destroy()
            self.build()

        buttons = ctk.CTkFrame(dialog, fg_color=BACKGROUND)
        buttons.pack(padx=24, pady=(8, 12), fill="x")
        ctk.CTkButton(
            buttons, text=self.text("cancel"), fg_color=CARD, hover_color=HOVER, command=dialog.destroy
        ).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(buttons, text=self.text("save"), command=save).pack(
            side="left", expand=True, padx=(4, 0)
        )

        if self.version:
            ctk.CTkLabel(dialog, text=self.text("version", version=self.version), text_color="#9a9a9a").pack(
                pady=(0, 12)
            )

    def open_new_profile_dialog(self) -> None:
        def create(name: str, icon: str) -> str | None:
            return validate_profile_name(name, self.profiles) or self.create_profile(name, icon)

        self.open_profile_dialog(self.text("new_profile"), self.text("create"), create)

    def open_edit_profile_dialog(self, name: str) -> None:
        def save(new_name: str, icon: str) -> str | None:
            if new_name != name:
                error = validate_profile_name(new_name, [other for other in self.profiles if other != name])
                if error:
                    return error
                self.write_profiles_ini(rename_profile(self.profiles_ini().read_text(), name, new_name))
                rename_icon(self.icons_file, name, new_name)
            save_icon(self.icons_file, new_name, icon)
            return None

        self.open_profile_dialog(
            self.text("edit_profile"),
            self.text("save"),
            save,
            name=name,
            icon=icon_for(load_icons(self.icons_file), name),
            on_delete=lambda edit_dialog: self.open_delete_dialog(name, edit_dialog),
        )

    def open_delete_dialog(self, name: str, edit_dialog: ctk.CTkToplevel) -> None:
        """Confirm the deletion by typing the profile name."""
        dialog = self.open_dialog(self.text("delete_title"))

        ctk.CTkLabel(
            dialog,
            text=self.text("delete_prompt", name=name),
            text_color=TEXT,
            justify="center",
        ).pack(padx=24, pady=(24, 12))

        typed_name = tk.StringVar()
        ctk.CTkEntry(dialog, textvariable=typed_name, width=320).pack(padx=24)

        error_label = ctk.CTkLabel(dialog, text="", text_color=ERROR)
        error_label.pack(padx=24, pady=(8, 0))

        def delete() -> None:
            if typed_name.get() != name:
                return
            error = self.delete_profile(name)
            if error:
                error_label.configure(text=self.text(error))
                return
            dialog.destroy()
            edit_dialog.destroy()
            self.build()

        buttons = ctk.CTkFrame(dialog, fg_color=BACKGROUND)
        buttons.pack(padx=24, pady=(8, 24), fill="x")
        ctk.CTkButton(
            buttons, text=self.text("cancel"), fg_color=CARD, hover_color=HOVER, command=dialog.destroy
        ).pack(side="left", expand=True, padx=(0, 4))
        delete_button = ctk.CTkButton(
            buttons,
            text=self.text("delete"),
            fg_color="#b33a3a",
            hover_color="#cc4444",
            state="disabled",
            command=delete,
        )
        delete_button.pack(side="left", expand=True, padx=(4, 0))
        typed_name.trace_add(
            "write",
            lambda *_: delete_button.configure(state="normal" if typed_name.get() == name else "disabled"),
        )

    def profiles_ini(self) -> Path:
        assert self.install is not None
        return self.install.profiles_dir / "profiles.ini"

    def write_profiles_ini(self, ini_text: str) -> None:
        """Save profiles.ini, keeping a copy of the previous version."""
        profiles_ini = self.profiles_ini()
        shutil.copy(profiles_ini, profiles_ini.with_name("profiles.ini.selector-bak"))
        profiles_ini.write_text(ini_text)

    def create_profile(self, name: str, icon: str) -> str | None:
        """Create the profile through Zen; returns an error key or None."""
        assert self.install is not None
        try:
            result = subprocess.run(
                create_profile_command(self.install, name), capture_output=True, timeout=60
            )
        except (OSError, subprocess.TimeoutExpired):
            return "zen_start_failed"
        if result.returncode != 0 or name not in read_profiles(self.install.profiles_dir):
            return "create_failed"
        save_icon(self.icons_file, name, icon)
        return None

    def delete_profile(self, name: str) -> str | None:
        """Remove the profile from profiles.ini and trash its folder; returns an error key or None."""
        profile_dir = Path(self.profiles[name])
        if profile_in_use(profile_dir):
            return "profile_in_use"
        try:
            new_ini = remove_profile(self.profiles_ini().read_text(), name)
        except ValueError as error:
            return str(error)
        if profile_dir.exists():
            try:
                send2trash(profile_dir)
            except OSError:
                return "trash_failed"
        self.write_profiles_ini(new_ini)
        remove_icon(self.icons_file, name)
        return None

    def launch_zen(self, profile_path: str) -> None:
        assert self.install is not None
        subprocess.Popen(launch_command(self.install, profile_path), start_new_session=True)
        self.root.after(500, self.root.quit)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="zen-profile-selector", description="Profile picker for Zen Browser."
    )
    parser.add_argument(
        "--install-desktop", action="store_true", help="add the selector to the applications menu"
    )
    parser.add_argument(
        "--uninstall-desktop", action="store_true", help="remove it from the applications menu"
    )
    args = parser.parse_args()
    if (args.install_desktop or args.uninstall_desktop) and sys.platform != "linux":
        parser.error("the applications menu entry is only supported on Linux")

    target = desktop_file(os.environ, Path.home())
    if args.install_desktop:
        install_desktop_entry(target, Path(sys.executable), ASSETS / "icon.png")
        print(f"Added to the applications menu: {target}")
        return
    if args.uninstall_desktop:
        removed = uninstall_desktop_entry(target)
        print("Removed from the applications menu." if removed else "It was not in the applications menu.")
        return

    root = ctk.CTk()
    ProfileSelector(root, config_dir(os.environ, Path.home()))
    root.mainloop()
