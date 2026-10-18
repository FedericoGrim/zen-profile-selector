from zen_profile_selector.i18n import (
    LANGUAGES,
    TRANSLATIONS,
    detect_language,
    translate,
    windows_display_locale,
)


def test_every_language_has_the_same_keys():
    english = set(TRANSLATIONS["en"])
    for language in LANGUAGES:
        assert set(TRANSLATIONS[language]) == english


def test_detects_supported_system_language():
    assert detect_language({"LANG": "it_IT.UTF-8"}) == "it"


def test_language_variables_follow_gettext_priority():
    env = {"LANGUAGE": "it:en", "LC_ALL": "", "LANG": "en_US.UTF-8"}
    assert detect_language(env) == "it"


def test_unsupported_or_missing_language_falls_back_to_english():
    assert detect_language({"LANG": "de_DE.UTF-8"}) == "en"
    assert detect_language({}) == "en"
    assert detect_language({"LANG": "C"}) == "en"


def test_translate_fills_placeholders():
    assert "Work" in translate("it", "delete_prompt", name="Work")


def test_unknown_language_uses_english():
    assert translate("xx", "create") == TRANSLATIONS["en"]["create"]


def test_windows_display_language_is_used_without_locale_variables():
    assert detect_language({}, system_locale="it_IT") == "it"


def test_locale_variables_win_over_the_windows_display_language():
    assert detect_language({"LANG": "en_US.UTF-8"}, system_locale="it_IT") == "en"


def test_unsupported_windows_display_language_falls_back_to_english():
    assert detect_language({}, system_locale="de_DE") == "en"
    assert detect_language({}, system_locale=None) == "en"


def test_windows_display_locale_is_none_elsewhere():
    assert windows_display_locale(system="linux") is None
