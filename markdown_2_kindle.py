import pypandoc
import os
import smtplib
import json
import logging
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

def get_md_files_in_directory(directory):
    """
    Get a list of all markdown (.md) files in the specified directory.
    """
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    logging.info(f"Found {len(md_files)} markdown files in directory {directory}")
    return md_files

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
    """
    title = extract_title_from_md(md_file)
    try:
        pypandoc.convert_file(md_file, 'epub', outputfile=output_epub, extra_args=[f'--metadata=title="{title}"'])
        logging.info(f"Successfully converted {md_file} to {output_epub} with title '{title}'")
    except Exception as e:
        logging.error(f"Error converting {md_file} to EPUB: {e}")

def send_email_with_attachment(epub_file, config):
    """
    Send the EPUB file to the specified Kindle email address via SMTP.
    """
    # Create email
    msg = MIMEMultipart()
    msg['From'] = config['smtp_user']
    msg['To'] = config['kindle_email']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg['Subject'] = f'New EPUB for Your Kindle ({current_time})'

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

    # Define the directory where markdown files are located
    md_directory = config["md_directory"]

    # Define output directory for EPUB files
    output_directory = config["output_directory"]
    os.makedirs(output_directory, exist_ok=True)

    # Get all markdown files in the directory
    md_files = get_md_files_in_directory(md_directory)

    # Convert each markdown file to EPUB and send via email
    for md_file in md_files:
        output_epub = os.path.join(output_directory, os.path.basename(md_file).replace(".md", ".epub"))
        convert_md_to_epub(md_file, output_epub)
        send_email_with_attachment(output_epub, config)

        # Delete the EPUB file after sending
        try:
            os.remove(output_epub)
            logging.info(f"Deleted {output_epub} after sending")
        except Exception as e:
            logging.error(f"Error deleting {output_epub}: {e}")

if __name__ == "__main__":
    main()
