# markdown-2-kindle

This project automates the conversion of Markdown (`.md`) files to EPUB format and prepares them for deployment to Kindle devices.

## Features
- Automatically scans a directory for Markdown files.
- Converts each Markdown file to an EPUB file using Pandoc.
- Sends the EPUB file to your Kindle email via SMTP.
- Includes the title from the first `#` heading and the latest Git commit ID (if available) in the email subject.
- Deletes the EPUB file after it has been sent.

## Requirements
- [Pandoc](https://pandoc.org/installing.html) must be installed on your system.
- Python dependencies are listed in `requirements.txt`.

## Configuration

1. Create a `config.json` file in the root of the repository with the following structure:

   ```json
   {
     "md_directory": "path/to/your/markdown/files",
     "output_directory": "path/to/output/epub/files",
     "kindle_email": "your-kindle-email@kindle.com",
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "smtp_user": "your-email@gmail.com",
     "smtp_password": "your-email-password"
   }
   ```

2. Replace the placeholders with your actual directory paths and SMTP credentials.

## Usage

1. You can specify the markdown directory either in `config.json` or by providing it as an argument:
   ```bash
   python markdown-2-kindle.py /path/to/your/markdown/files
   ```

2. If no directory is provided, it defaults to the one specified in `config.json`.

3. The script will:
   - Convert the markdown files to EPUB.
   - Send the EPUB to your Kindle email.
   - Include the title from the markdown and the latest Git commit ID (if the directory is within a Git repository) in the email subject.
   - Delete the EPUB file after sending.
