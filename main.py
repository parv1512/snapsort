"""
Sort iPhone‑imported photos & videos into Year → Month folders.
Asks the user for source and destination paths at runtime.
"""

import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# -------------------------------------------------
# Optional: use exifread for HEIC/JPG EXIF (install with pip)
# -------------------------------------------------
try:
    import exifread
except ImportError:          # pragma: no cover
    exifread = None
    print("Warning: exifread not installed – falling back to file modification time.")

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def ask_path(prompt: str) -> Path:
    """Ask the user for a folder path and return a Path object."""
    while True:
        raw = input(f"{prompt}: ").strip()
        if not raw:
            print("  → Please enter a path.")
            continue
        p = Path(raw).expanduser().resolve()
        if not p.exists():
            print("  → Folder does not exist. Try again.")
            continue
        if not p.is_dir():
            print("  → Not a directory. Try again.")
            continue
        return p


def log(msg: str, logfile):
    print(msg)
    logfile.write(msg + "\n")


def get_image_date(image_path: Path, logfile):
    """Read EXIF DateTimeOriginal → fallback to file mtime."""
    if exifread:
        try:
            with image_path.open('rb') as f:
                tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
                dt = tags.get('EXIF DateTimeOriginal')
                if dt:
                    return datetime.strptime(str(dt), '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            log(f"  [EXIF error] {image_path.name}: {e}", logfile)

    # Fallback to file modification time
    try:
        return datetime.fromtimestamp(image_path.stat().st_mtime)
    except Exception as e:
        log(f"  [mtime error] {image_path.name}: {e}", logfile)
        return None


def file_hash(path: Path) -> str:
    """MD5 hash of the file (used for duplicate detection)."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_move(src: Path, dst: Path, logfile):
    """Copy (preserving metadata) → rename on conflict."""
    try:
        shutil.copy2(src, dst)                     # copy2 keeps timestamps & EXIF
        log(f"  → {dst.relative_to(DEST_ROOT)}", logfile)
    except Exception as e:
        log(f"  [copy error] {src.name}: {e}", logfile)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    global DEST_ROOT
    print("\n=== iPhone Photo Sorter ===\n")

    SOURCE = ask_path("Source folder (where the iPhone photos are now)")
    DEST_ROOT = ask_path("Destination root (where you want the sorted folders)")

    # Create log inside destination
    log_path = DEST_ROOT / "sort_log.txt"
    logfile = log_path.open("w", encoding="utf-8")
    log(f"Source : {SOURCE}", logfile)
    log(f"Destination : {DEST_ROOT}", logfile)
    log("-" * 50, logfile)

    # Extensions we care about
    IMG_EXT = {'.jpg', '.jpeg', '.png', '.heic', '.tif', '.tiff'}
    VID_EXT = {'.mov', '.mp4', '.avi', '.m4v'}

    seen_hashes = set()

    for root, _, files in os.walk(SOURCE):
        for name in files:
            src_path = Path(root) / name
            ext = src_path.suffix.lower()

            if ext not in IMG_EXT and ext not in VID_EXT:
                continue

            if src_path.stat().st_size == 0:
                log(f"  [skip empty] {src_path.name}", logfile)
                continue

            # ---------- date ----------
            if ext in IMG_EXT:
                dt = get_image_date(src_path, logfile)
            else:   # video → use newest of ctime/mtime
                c = src_path.stat().st_ctime
                m = src_path.stat().st_mtime
                dt = datetime.fromtimestamp(max(c, m))

            if not dt:
                log(f"  [no date] {src_path.name}", logfile)
                continue

            year = dt.strftime("%Y")
            month_num = dt.strftime("%m")
            month_name = dt.strftime("%B")
            target_dir = DEST_ROOT / year / f"{year}-{month_num}_{month_name}"
            target_dir.mkdir(parents=True, exist_ok=True)

            # ---------- duplicate check ----------
            h = file_hash(src_path)
            if h in seen_hashes:
                log(f"  [duplicate] {src_path.name}", logfile)
                continue
            seen_hashes.add(h)

            # ---------- destination filename ----------
            dst_path = target_dir / name
            if dst_path.exists():
                base, suffix = name.rsplit('.', 1) if '.' in name else (name, '')
                i = 1
                while True:
                    new_name = f"{base}_{i}.{suffix}" if suffix else f"{base}_{i}"
                    dst_path = target_dir / new_name
                    if not dst_path.exists():
                        break
                    i += 1

            safe_move(src_path, dst_path, logfile)

    logfile.close()
    print("\nFinished! Log saved to:", log_path)


if __name__ == "__main__":
    main()