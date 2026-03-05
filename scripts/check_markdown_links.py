from __future__ import annotations

import re
import sys
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
IGNORED_PREFIXES = ("http://", "https://", "mailto:", "#")


def extract_links(text: str) -> list[str]:
    return [m.group(1).strip() for m in LINK_RE.finditer(text)]


def is_local_link(link: str) -> bool:
    return not link.startswith(IGNORED_PREFIXES)


def normalize_target(link: str) -> str:
    return link.split("#", 1)[0].strip()


def check_markdown_file(md_file: Path, root: Path) -> list[str]:
    errors: list[str] = []
    text = md_file.read_text(encoding="utf-8")
    for link in extract_links(text):
        if not is_local_link(link):
            continue
        target = normalize_target(link)
        if not target:
            continue
        target_path = (md_file.parent / target).resolve()
        if (
            not target_path.exists()
            or root not in target_path.parents
            and target_path != root
        ):
            errors.append(f"{md_file}: broken local link -> {link}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    markdown_files = [p for p in root.rglob("*.md") if ".git" not in p.parts]
    all_errors: list[str] = []
    for md in markdown_files:
        all_errors.extend(check_markdown_file(md, root))

    if all_errors:
        print("Broken markdown links found:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print(f"Markdown link check passed ({len(markdown_files)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
