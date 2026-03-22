"""Launch an interactive Claude Code session with a prompt from a temp file."""
import os
import subprocess
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: claude_launcher.py <prompt_file>", file=sys.stderr)
        sys.exit(1)

    prompt_file = sys.argv[1]
    try:
        with open(prompt_file, encoding="utf-8") as f:
            prompt = f.read().strip()
        os.remove(prompt_file)
    except FileNotFoundError:
        print(f"Prompt file not found: {prompt_file}", file=sys.stderr)
        sys.exit(1)

    subprocess.run(["claude", "--model", "sonnet", prompt])


if __name__ == "__main__":
    main()
