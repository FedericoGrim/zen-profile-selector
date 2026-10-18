from __future__ import annotations

import locale
import sys
from collections.abc import Mapping

DEFAULT_LANGUAGE = "en"
LANGUAGES = {"en": "English", "it": "Italiano"}

TRANSLATIONS = {
    "en": {
        "new_card": "New",
        "new_profile": "New profile",
        "edit_profile": "Edit profile",
        "profile_name": "Profile name",
        "create": "Create",
        "save": "Save",
        "cancel": "Cancel",
        "delete_profile_button": "Delete profile…",
        "delete_title": "Delete profile",
        "delete": "Delete",
        "delete_prompt": "Type «{name}» to delete this profile.\nIts folder will be moved to the Trash.",
        "zen_not_found": "Zen Browser not found. Set it up in ⚙ Settings.",
        "settings_title": "Settings",
        "zen_command_label": "Zen command",
        "profiles_dir_label": "Profiles folder",
        "settings_hint": "Leave a field empty to detect it automatically.",
        "browse": "Browse…",
        "auto_detect": "Detect automatically",
        "version": "Version {version}",
        "check_updates": "Check for updates at startup",
        "update_available": "Version {version} is available. Update with:\n{command}",
        "copy_command": "Copy command",
        "copied": "Copied",
        "update_ready": "Version {version} is available.",
        "update": "Update",
        "updating": "Updating…",
        "update_done": "Updated to version {version}. Restart to use it.",
        "restart": "Restart",
        "update_failed": "The update failed. Run it in a terminal:\n{command}",
        "profiles_dir_invalid": "This folder has no profiles.ini",
        "zen_command_not_found": "Command not found",
        "zen_command_invalid": "Invalid command",
        "empty_name": "Enter a name for the profile",
        "duplicate_name": "A profile with this name already exists",
        "last_profile": "The last profile cannot be deleted",
        "profile_in_use": "Close Zen before deleting this profile",
        "trash_failed": "Could not move the profile folder to the Trash",
        "zen_start_failed": "Could not run Zen to create the profile",
        "create_failed": "Zen did not create the profile",
    },
    "it": {
        "new_card": "Nuovo",
        "new_profile": "Nuovo profilo",
        "edit_profile": "Modifica profilo",
        "profile_name": "Nome del profilo",
        "create": "Crea",
        "save": "Salva",
        "cancel": "Annulla",
        "delete_profile_button": "Elimina profilo…",
        "delete_title": "Elimina profilo",
        "delete": "Elimina",
        "delete_prompt": "Per eliminare il profilo scrivi «{name}».\nLa sua cartella finirà nel Cestino.",
        "zen_not_found": "Zen Browser non trovato. Configuralo in ⚙ Impostazioni.",
        "settings_title": "Impostazioni",
        "zen_command_label": "Comando di Zen",
        "profiles_dir_label": "Cartella dei profili",
        "settings_hint": "Lascia vuoto un campo per rilevarlo automaticamente.",
        "browse": "Sfoglia…",
        "auto_detect": "Rileva automaticamente",
        "version": "Versione {version}",
        "check_updates": "Controlla gli aggiornamenti all'avvio",
        "update_available": "È disponibile la versione {version}. Aggiorna con:\n{command}",
        "copy_command": "Copia comando",
        "copied": "Copiato",
        "update_ready": "È disponibile la versione {version}.",
        "update": "Aggiorna",
        "updating": "Aggiornamento…",
        "update_done": "Aggiornato alla versione {version}. Riavvia per usarla.",
        "restart": "Riavvia",
        "update_failed": "Aggiornamento non riuscito. Eseguilo in un terminale:\n{command}",
        "profiles_dir_invalid": "Questa cartella non contiene profiles.ini",
        "zen_command_not_found": "Comando non trovato",
        "zen_command_invalid": "Comando non valido",
        "empty_name": "Scrivi un nome per il profilo",
        "duplicate_name": "Esiste già un profilo con questo nome",
        "last_profile": "Non si può eliminare l'ultimo profilo",
        "profile_in_use": "Chiudi Zen prima di eliminare questo profilo",
        "trash_failed": "Impossibile spostare la cartella nel Cestino",
        "zen_start_failed": "Impossibile avviare Zen per creare il profilo",
        "create_failed": "Zen non ha creato il profilo",
    },
}


def windows_display_locale(system: str = sys.platform) -> str | None:
    """Windows display language as a locale name such as it_IT; None on other systems."""
    if system != "win32":
        return None
    import ctypes

    language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()  # type: ignore[attr-defined]
    return locale.windows_locale.get(language_id)


def detect_language(env: Mapping[str, str], system_locale: str | None = None) -> str:
    """First supported language from the usual locale variables, then from the system locale (the
    Windows display language, since Windows sets no locale variables), English otherwise."""
    candidates = [
        name
        for variable in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
        for name in env.get(variable, "").split(":")
    ]
    for name in [*candidates, system_locale or ""]:
        code = name[:2].lower()
        if code in LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


def translate(language: str, key: str, **values: str) -> str:
    texts = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])
    return texts[key].format(**values)
