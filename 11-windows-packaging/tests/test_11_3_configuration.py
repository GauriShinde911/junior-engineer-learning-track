import json
import sys
from pathlib import Path
import pytest

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "11.3-configuration"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

import app_with_external_config as ext_cfg


# ── find_config_file ─────────────────────────────────────────────────────────

def test_find_config_file_beside_exe(tmp_path, monkeypatch):
    """Config file placed next to __file__ (dev mode path) is found."""
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text("{}", encoding="utf-8")

    # Patch __file__ resolution by monkey-patching the module's find function
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)
    assert ext_cfg.find_config_file() == config_file


def test_find_config_file_returns_none_when_missing(monkeypatch):
    """Returns None when config file is absent from both search locations."""
    monkeypatch.delenv("APPDATA", raising=False)
    # Temporarily set module __file__ to a directory without the config
    original = ext_cfg.__file__

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.setattr(ext_cfg, "__file__", str(Path(td) / "fake_module.py"))
        result = ext_cfg.find_config_file()
    assert result is None


# ── load_config ──────────────────────────────────────────────────────────────

def test_load_config_exits_if_no_file(monkeypatch):
    """load_config raises SystemExit(2) when no config file exists."""
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: None)
    monkeypatch.delenv("APPDATA", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        ext_cfg.load_config()
    assert exc_info.value.code == 2


def test_load_config_error_message_mentions_file(monkeypatch, capsys):
    """The SystemExit error message tells the user what file to create."""
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: None)
    monkeypatch.delenv("APPDATA", raising=False)
    with pytest.raises(SystemExit):
        ext_cfg.load_config()
    err = capsys.readouterr().err
    assert ext_cfg.CONFIG_FILENAME in err


def test_load_config_merges_defaults_with_user_values(tmp_path, monkeypatch):
    """User config overrides specific keys; missing keys come from defaults."""
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text(json.dumps({"max_results": 5}), encoding="utf-8")
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)

    config = ext_cfg.load_config()
    assert config["max_results"] == 5                        # User override
    assert config["log_level"] == "INFO"                     # Default retained
    assert config["app_title"] == ext_cfg.DEFAULT_CONFIG["app_title"]


def test_load_config_exits_on_invalid_json(tmp_path, monkeypatch):
    """Malformed JSON config exits with code 2 and a readable message."""
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text("{bad json", encoding="utf-8")
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)

    with pytest.raises(SystemExit) as exc_info:
        ext_cfg.load_config()
    assert exc_info.value.code == 2


def test_load_config_empty_json_object_is_valid(tmp_path, monkeypatch):
    """An empty JSON object {} is a valid config (all values from defaults)."""
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)

    config = ext_cfg.load_config()
    assert config == ext_cfg.DEFAULT_CONFIG


# ── run_external_config (integration) ────────────────────────────────────────

def test_run_external_config_prints_to_stdout(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text(json.dumps({"max_results": 3}), encoding="utf-8")
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)

    text_file = tmp_path / "input.txt"
    text_file.write_text("the cat sat on the mat\n", encoding="utf-8")
    ext_cfg.run_external_config(str(text_file))

    out = capsys.readouterr().out
    assert "the" in out
    assert "cat" in out


def test_run_external_config_writes_to_output_dir(tmp_path, monkeypatch, capsys):
    out_dir = tmp_path / "output"
    config_file = tmp_path / ext_cfg.CONFIG_FILENAME
    config_file.write_text(
        json.dumps({"max_results": 2, "output_dir": str(out_dir)}),
        encoding="utf-8"
    )
    monkeypatch.setattr(ext_cfg, "find_config_file", lambda: config_file)

    text_file = tmp_path / "input.txt"
    text_file.write_text("hello world hello\n", encoding="utf-8")
    ext_cfg.run_external_config(str(text_file))

    summary_file = out_dir / "input_summary.txt"
    assert summary_file.exists()
    content = summary_file.read_text(encoding="utf-8")
    assert "hello" in content


# ── bad_config (contrast test) ───────────────────────────────────────────────

def test_bad_config_uses_hardcoded_values():
    """Verify app_with_bad_config.py exposes baked-in constants (contrast test)."""
    import app_with_bad_config as bad
    assert isinstance(bad.OUTPUT_DIR, str)
    assert isinstance(bad.MAX_RESULTS, int)
    assert isinstance(bad.LOG_LEVEL, str)
    # The values are not configurable at runtime — they are module-level literals.
    assert bad.OUTPUT_DIR == "C:\\Users\\admin\\wc_output"
