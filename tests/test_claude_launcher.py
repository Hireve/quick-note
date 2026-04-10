import subprocess

import pytest

import claude_launcher


def test_run_claude_passes_prompt_via_stdin(monkeypatch):
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = claude_launcher.run_claude("hello from prompt")

    assert result.returncode == 0
    assert captured["args"] == ["claude", "--model", "sonnet"]
    assert captured["kwargs"].get("input") == "hello from prompt"
    assert captured["kwargs"].get("text") is True


def test_main_deletes_prompt_file_after_success(tmp_path, monkeypatch):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("ship it", encoding="utf-8")

    monkeypatch.setattr(
        claude_launcher,
        "run_claude",
        lambda prompt: subprocess.CompletedProcess(args=["claude"], returncode=0),
    )

    with pytest.raises(SystemExit) as exc_info:
        claude_launcher.main(["claude_launcher.py", str(prompt_file)])

    assert exc_info.value.code == 0
    assert not prompt_file.exists()


def test_main_preserves_prompt_file_on_nonzero_exit(tmp_path, monkeypatch, capsys):
    """Prompt file must be preserved when Claude exits with a nonzero return code."""
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("my important prompt", encoding="utf-8")

    monkeypatch.setattr(
        claude_launcher,
        "run_claude",
        lambda prompt: subprocess.CompletedProcess(args=["claude"], returncode=1),
    )

    with pytest.raises(SystemExit) as exc_info:
        claude_launcher.main(["claude_launcher.py", str(prompt_file)])

    assert exc_info.value.code == 1
    assert prompt_file.exists()
    assert str(prompt_file) in capsys.readouterr().err


def test_main_preserves_prompt_file_when_claude_missing(tmp_path, monkeypatch, capsys):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("keep me", encoding="utf-8")

    def fake_run(prompt):
        raise FileNotFoundError

    monkeypatch.setattr(claude_launcher, "run_claude", fake_run)

    with pytest.raises(SystemExit) as exc_info:
        claude_launcher.main(["claude_launcher.py", str(prompt_file)])

    assert exc_info.value.code == 1
    assert prompt_file.exists()
    assert str(prompt_file) in capsys.readouterr().err
