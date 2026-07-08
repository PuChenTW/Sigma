from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_SUBJECT_LENGTH = 72
VALID_TYPES = {
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "style",
    "test",
}

SUBJECT_RE = re.compile(rf"^({'|'.join(sorted(VALID_TYPES))})(\([a-z0-9][a-z0-9-]*\))?!?: [^\s].+$")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_commit_message.py <commit-msg-file>", file=sys.stderr)
        return 2

    message_path = Path(sys.argv[1])
    subject = first_meaningful_line(message_path)
    if subject is None:
        print("commit message is empty", file=sys.stderr)
        return 1

    if is_generated_commit(subject):
        return 0

    if len(subject) > MAX_SUBJECT_LENGTH:
        print(f"commit subject must be <= {MAX_SUBJECT_LENGTH} characters", file=sys.stderr)
        return 1

    if not SUBJECT_RE.match(subject):
        allowed = ", ".join(sorted(VALID_TYPES))
        print("commit subject must follow Conventional Commits: <type>(optional-scope): <summary>", file=sys.stderr)
        print(f"allowed types: {allowed}", file=sys.stderr)
        print("example: feat(api): add project evidence endpoint", file=sys.stderr)
        return 1

    return 0


def first_meaningful_line(message_path: Path) -> str | None:
    for line in message_path.read_text(encoding="utf-8").splitlines():
        subject = line.strip()
        if subject and not subject.startswith("#"):
            return subject
    return None


def is_generated_commit(subject: str) -> bool:
    prefixes = (
        "Merge ",
        "Revert ",
        "fixup! ",
        "squash! ",
    )
    return subject.startswith(prefixes)


if __name__ == "__main__":
    raise SystemExit(main())
