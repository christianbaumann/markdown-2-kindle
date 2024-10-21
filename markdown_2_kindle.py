import pypandoc
import os
import smtplib
import json
import logging
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file):
    """
    Load email and SMTP settings from config.json.
    """
    with open(config_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_changed_md_files(md_directory):
    """
    Get a list of all new or changed markdown (.md) files since the last commit,
    excluding files that contain 'prompt' in their filename.
    """
    try:
        changed_files_output = subprocess.check_output(
            ['git', 'diff', '--name-only', 'HEAD'], cwd=md_directory
        ).decode('utf-8').splitlines()

        # Filter markdown files and exclude those containing 'prompt'
        md_files = [
            os.path.join(md_directory, file)
            for file in changed_files_output
            if file.endswith(".md") and "prompt" not in file
        ]

        logging.info(f"Found {len(md_files)} changed markdown files (excluding 'prompt') since the last commit")
        return md_files
    except subprocess.CalledProcessError:
        logging.warning(f"{md_directory} is not a Git repository or Git is not installed.")
        return []

def extract_title_from_md(md_file):
    """
    Extract the first H1 (#) heading from the markdown file as the title.
    """
    with open(md_file, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('# '):
                return line[2:].strip()
    return 'Untitled'  # Fallback if no title is found

def convert_md_to_epub(md_file, output_epub):
    """
    Convert a markdown file to an EPUB file using pypandoc, extracting the title from the markdown.
    Apply custom CSS to ensure no background color is used.
    """
    title = extract_title_from_md(md_file)
    css_file = 'epub-style.css'
    try:
        pypandoc.convert_file(md_file, 'epub', outputfile=output_epub, extra_args=[
            f'--metadata=title="{title}"', f'--css={css_file}'
        ])
        logging.info(f"Successfully converted {md_file} to {output_epub} with title '{title}'")
    except Exception as e:
        logging.error(f"Error converting {md_file} to EPUB: {e}")
    return title

def get_git_commit_id(md_directory):
    """
    Get the latest Git commit ID if the directory is part of a Git repository.
    """
    try:
        commit_id = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=md_directory).strip().decode('utf-8')
        logging.info(f"Latest commit ID: {commit_id}")
        return commit_id
    except subprocess.CalledProcessError:
        logging.warning(f"{md_directory} is not a Git repository or Git is not installed.")
        return None

def send_email_with_attachment(epub_file, config, commit_id=None, title=None):
    """
    Send the EPUB file to the specified Kindle email address via SMTP, with optional Git commit ID and EPUB title in the subject.
    """
    # Create email
    msg = MIMEMultipart()
    msg['From'] = config['smtp_user']
    msg['To'] = config['kindle_email']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'New EPUB "{title}" for Your Kindle ({current_time})'
    if commit_id:
        subject += f' [Commit: {commit_id}]'
    msg['Subject'] = subject

    # Attach the EPUB file
    attachment = MIMEBase('application', 'octet-stream')
    with open(epub_file, 'rb') as file:
        attachment.set_payload(file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(epub_file)}')
    msg.attach(attachment)

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['smtp_user'], config['smtp_password'])
        server.sendmail(config['smtp_user'], config['kindle_email'], msg.as_string())
        server.quit()
        logging.info(f"Successfully sent {epub_file} to {config['kindle_email']}")
    except Exception as e:
        logging.error(f"Error sending {epub_file} to {config['kindle_email']}: {e}")

def main():
    # Load config settings from config.json
    config = load_config('config.json')
    logging.info("Loaded configuration")

    # Set the markdown directory from ARGV if provided, otherwise use the one from config
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        md_directory = sys.argv[1]
        logging.info(f"Using directory from ARGV: {md_directory}")
    else:
        md_directory = config["md_directory"]
        logging.info(f"Using directory from config: {md_directory}")

    # Define output directory for EPUB files
    output_directory = config["output_directory"]
    os.makedirs(output_directory, exist_ok=True)

    # Check for Git repository and get latest commit ID if available
    commit_id = get_git_commit_id(md_directory)

    # Get all changed markdown files in the directory since the last commit
    changed_md_files = get_changed_md_files(md_directory)

    if not changed_md_files:
        logging.info("No new or changed markdown files to process.")
        return

    # Convert each changed markdown file to EPUB and send via email
    for md_file in changed_md_files:
        output_epub = os.path.join(output_directory, os.path.basename(md_file).replace(".md", ".epub"))
        title = convert_md_to_epub(md_file, output_epub)
        send_email_with_attachment(output_epub, config, commit_id, title)

        # Delete the EPUB file after sending
        try:
            os.remove(output_epub)
            logging.info(f"Deleted {output_epub} after sending")
        except Exception as e:
            logging.error(f"Error deleting {output_epub}: {e}")

if __name__ == "__main__":
    main()
