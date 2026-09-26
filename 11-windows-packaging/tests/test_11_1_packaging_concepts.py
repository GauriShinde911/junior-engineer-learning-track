import sys
from pathlib import Path
import pytest

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "11.1-packaging-concepts"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from sample_cli import count_text, top_words, format_report, run, parse_args


# ── count_text ──────────────────────────────────────────────────────────────

def test_count_text_basic():
    result = count_text("hello world\nfoo bar\n")
    assert result["words"] == 4
    assert result["lines"] == 2
    assert result["chars"] == 20


def test_count_text_empty_string():
    result = count_text("")
    assert result["words"] == 0
    assert result["lines"] == 0
    assert result["chars"] == 0


def test_count_text_single_line_no_trailing_newline():
    result = count_text("one two three")
    assert result["lines"] == 1
    assert result["words"] == 3


def test_count_text_only_newlines():
    result = count_text("\n\n\n")
    assert result["lines"] == 3
    assert result["words"] == 0


# ── top_words ────────────────────────────────────────────────────────────────

def test_top_words_ranking():
    content = "the cat sat on the mat the cat"
    result = top_words(content, 2)
    assert result[0] == ("the", 3)
    assert result[1] == ("cat", 2)


def test_top_words_case_insensitive():
    content = "Python python PYTHON"
    result = top_words(content, 1)
    assert result[0][0] == "python"
    assert result[0][1] == 3


def test_top_words_strips_punctuation():
    content = "hello, world! hello."
    result = top_words(content, 1)
    assert result[0] == ("hello", 2)


def test_top_words_n_greater_than_vocab():
    content = "one two three"
    result = top_words(content, 10)
    assert len(result) == 3


# ── parse_args ───────────────────────────────────────────────────────────────

def test_parse_args_defaults():
    args = parse_args(["somefile.txt"])
    assert args.filepath == "somefile.txt"
    assert args.top == 0
    assert args.no_header is False


def test_parse_args_top_flag():
    args = parse_args(["somefile.txt", "--top", "5"])
    assert args.top == 5


def test_parse_args_no_header_flag():
    args = parse_args(["somefile.txt", "--no-header"])
    assert args.no_header is True


# ── run (integration) ────────────────────────────────────────────────────────

def test_run_with_real_file(tmp_path, capsys):
    f = tmp_path / "test.txt"
    f.write_text("hello world\nhello python\n", encoding="utf-8")
    exit_code = run([str(f)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Words" in out
    assert "Lines" in out


def test_run_file_not_found(capsys):
    exit_code = run(["nonexistent_file_xyz.txt"])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_run_top_words_output(tmp_path, capsys):
    f = tmp_path / "data.txt"
    f.write_text("the quick brown fox the fox\n", encoding="utf-8")
    exit_code = run([str(f), "--top", "2"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "the" in out
    assert "fox" in out


def test_run_no_header_suppresses_title(tmp_path, capsys):
    f = tmp_path / "data.txt"
    f.write_text("hello world\n", encoding="utf-8")
    run([str(f), "--no-header"])
    out = capsys.readouterr().out
    assert "wc-summary" not in out
