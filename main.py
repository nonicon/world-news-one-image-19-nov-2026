"""World News in One Image — 19 November 2026.

The entry program for the make.fun news-image competition: it places the
pre-rendered front page (entry.png, drawn at build time) into the output
directory the harness reads. Pure standard library, no network access."""

from os import environ
from pathlib import Path

IMAGE_NAME = "entry.png"
DEFAULT_OUTPUT = "/output"


def locate_image() -> Path:
    """Return the path of the front-page image shipped beside this file."""
    return Path(__file__).resolve().parent / IMAGE_NAME


def choose_output_dir() -> Path:
    """Return the harness output directory, defaulting to /output."""
    return Path(environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT))


def main() -> int:
    """Copy the front-page image to the harness output directory."""
    source = locate_image()
    target = choose_output_dir()
    target.mkdir(parents=True, exist_ok=True)
    (target / IMAGE_NAME).write_bytes(source.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
