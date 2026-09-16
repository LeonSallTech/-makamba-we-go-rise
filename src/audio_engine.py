#!/usr/bin/env python3

from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parent.parent
PROJECT_FILE = ROOT / "project.json"
OUTPUT_DIR = ROOT / "output"


def load_project():
    with PROJECT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def require_tool(name):
    path = shutil.which(name)

    if not path:
        raise RuntimeError(f"Required audio tool not found: {name}")

    return path


def show_environment():
    project = load_project()

    print("=" * 60)
    print("MAKAMBA WE GO RISE — AUDIO ENGINE")
    print("=" * 60)

    print("Project :", project["project"])
    print("Version :", project["version"])
    print("Style   :", ", ".join(project["style"]))

    print()
    print("AUDIO TOOLS")
    print("-" * 60)

    print("ffmpeg  :", require_tool("ffmpeg"))
    print("ffprobe :", require_tool("ffprobe"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("OUTPUT")
    print("-" * 60)
    print("Directory:", OUTPUT_DIR)

    print()
    print("ENGINE STATUS: READY")
    print("=" * 60)


if __name__ == "__main__":
    try:
        show_environment()
    except Exception as exc:
        print("ENGINE ERROR:", exc)
        raise SystemExit(1)
