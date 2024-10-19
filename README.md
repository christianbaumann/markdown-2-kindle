# markdown-2-kindle

This project automates the conversion of Markdown (`.md`) files to EPUB format and prepares them for deployment to Kindle devices.

## Features
- Automatically scans a directory for Markdown files.
- Converts each Markdown file to an EPUB file using Pandoc.
- Sends the EPUB file to your Kindle email via SMTP.

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
