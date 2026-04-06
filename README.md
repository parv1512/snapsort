# SnapSort

SnapSort is a Python tool that automatically organizes iPhone photos and videos into structured Year → Month folders based on their metadata.

## Features

- Organizes media into Year/Year-Month folders
- Uses EXIF metadata for accurate photo dates
- Handles videos using file timestamps
- Detects and skips duplicate files using MD5 hashing
- Preserves original metadata during copy
- Generates a detailed log file
- Falls back to file modification time if EXIF data is unavailable

## Folder Structure

Destination/
├── 2023/
│   ├── 2023-01_January/
│   ├── 2023-02_February/
├── 2024/
│   ├── 2024-06_June/

## Installation

1. Clone the repository:

   git clone https://github.com/your-username/snapsort.git  
   cd snapsort

2. Install dependencies (optional but recommended):

   pip install exifread

If exifread is not installed, the script will use file modification time instead.

## Usage

Run the script:

   python main.py

You will be prompted to enter:
- Source folder (where your photos/videos are located)
- Destination folder (where sorted files will be stored)

## Supported File Types

Images:
.jpg, .jpeg, .png, .heic, .tif, .tiff

Videos:
.mov, .mp4, .avi, .m4v

## How It Works

- Recursively scans all files in the source folder
- Extracts date information:
  - Images: EXIF DateTimeOriginal
  - Videos: Latest of creation or modification time
- Creates a Year → Month folder structure
- Detects duplicates using file hashing
- Copies files while preserving metadata
- Logs all actions

## Log File

A file named sort_log.txt is created in the destination folder.  
It contains details about processed files, duplicates, and any errors.

## Notes

- Files are copied, not moved
- Duplicate detection is based on file content, not filename
- Best used with original iPhone exports

## License

MIT License
