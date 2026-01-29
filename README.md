# VidRecover

VidRecover is a Python-based utility designed to automate and simplify the process of restoring media files from LTO tapes. It bridges the gap between media inventory (CSV) and editing timelines (XML), helping archivists and editors efficiently locate and retrieve specific footage.

## Features

- **Media Analysis**: Parses editing XML files (e.g., from DaVinci Resolve or Premiere Pro) to identify required media assets.
- **Inventory Search**: Cross-references needed files against a master CSV inventory of LTO tapes.
- **Tape Optimization**: Groups files by tape to minimize physically swapping cartridges.
- **Interactive Restoration**: Guides the user through the mounting process and handles file copying with metadata preservation.

## Usage

### 1. Identify Tapes
Use `extract_lto_tapes.py` to simply list which tapes contain your media.

```bash
python3 extract_lto_tapes.py "INVENTORY.CSV" --xml "TIMELINE.xml"
```

### 2. Restore Media
Use `restore_media.py` to start the interactive restoration process.

```bash
python3 restore_media.py "INVENTORY.CSV" --xml "TIMELINE.xml" --dest "/path/to/restoration/folder"
```
