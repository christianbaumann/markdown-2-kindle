# markdown-2-kindle

This project automates the conversion of Markdown (`.md`) files to EPUB format and prepares them for deployment to Kindle devices.

## Features
- Automatically scans a directory for Markdown files.
- Converts each Markdown file to an EPUB file using Pandoc.
- Supports directory-level processing and output file management.

## Requirements
- [Pandoc](https://pandoc.org/installing.html) must be installed on your system.
- Python dependencies are listed in `requirements.txt`.

## Usage

1. Place your markdown files in the desired directory.
2. Modify the `markdown-2-kindle.py` script to specify the path to your markdown files and the output directory for EPUB files.
3. Run the script:
   ```bash
   python markdown-2-kindle.py
   ```
