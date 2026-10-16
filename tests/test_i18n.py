from zen_profile_selector.i18n import LANGUAGES, TRANSLATIONS, detect_language, translate


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
