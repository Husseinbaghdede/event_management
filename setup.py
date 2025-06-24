#!/usr/bin/env python3
"""
Event Scheduler project bootstrapper.

Creates the full folder / file layout, leaving all files empty
(except for __init__.py placeholders). Run once from the project root:

    $ python setup.py
"""
from pathlib import Path

# ---------------------------------------------------------------------
# Define the desired structure: {relative_folder: [file, file, ...]}
# ---------------------------------------------------------------------
STRUCTURE = {
    "": ["app.py", "requirements.txt", ".env", "README.md"],
    "static/css": ["style.css"],
    "static/js": ["main.js"],
    "static/images": [],           # keep empty for now
    "templates": [
        "base.html",
        "index.html",
        "add_event.html",
        "search.html",
    ],
    "models": ["event.py"],
    "routes": ["__init__.py", "events.py", "search.py"],
    "services": ["__init__.py", "database.py", "ai_service.py"],
    "data": ["events.db"],         # empty SQLite file
}

# ---------------------------------------------------------------------
def create_skeleton(root: Path) -> None:
    """
    Recursively build the folder & file skeleton under *root*.
    """
    for rel_dir, files in STRUCTURE.items():
        dir_path = root / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)

        for filename in files:
            file_path = dir_path / filename
            if file_path.exists():
                continue  # leave existing content untouched

            file_path.touch()

            # Insert a tiny stub where sensible
            if filename == "__init__.py":
                file_path.write_text("# Package initializer\n")

    print(f"✔  Project skeleton ready at: {root.resolve()}")


# ---------------------------------------------------------------------
if __name__ == "__main__":
    project_root = Path(__file__).parent
    create_skeleton(project_root)
