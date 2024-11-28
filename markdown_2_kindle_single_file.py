import pypandoc
import os
import smtplib
import json
import logging
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from email.mime.text import MIMEText

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file):
    """
    Load email and SMTP settings from config.json.
    """
    with open(config_file, 'r', encoding='utf-8') as file:
        return json.load(file)

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

def send_email_with_attachment(epub_file, config, title=None):
    """
    Send the EPUB file to the specified Kindle email address via SMTP, with optional EPUB title in the subject.
    """
    # Create email
    msg = MIMEMultipart()
    msg['From'] = config['smtp_user']
    msg['To'] = config['kindle_email']
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'New EPUB "{title}" for Your Kindle ({current_time})'
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

    # Check if a markdown file path is provided via command line
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        md_file = sys.argv[1]
        logging.info(f"Using markdown file from ARGV: {md_file}")
    else:
        logging.error("Please provide the path to a markdown (.md) file as a command line argument.")
        sys.exit(1)

    # Define output EPUB file path
    output_directory = config.get("output_directory", "output")
    os.makedirs(output_directory, exist_ok=True)
    output_epub = os.path.join(output_directory, os.path.basename(md_file).replace(".md", ".epub"))

    # Convert markdown to EPUB
    title = convert_md_to_epub(md_file, output_epub)

    # Send the EPUB via email
    send_email_with_attachment(output_epub, config, title)

    # Delete the EPUB file after sending
    try:
        os.remove(output_epub)
        logging.info(f"Deleted {output_epub} after sending")
    except Exception as e:
        logging.error(f"Error deleting {output_epub}: {e}")

if __name__ == "__main__":
    main()
