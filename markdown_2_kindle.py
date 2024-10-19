import pypandoc
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText

def load_config(config_file):
    """
    Load email and SMTP settings from config.json.
    """
    with open(config_file, 'r') as file:
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
    return md_files

def convert_md_to_epub(md_file, output_epub):
    """
    Convert a markdown file to an EPUB file using pypandoc.
    """
    try:
        pypandoc.convert_file(md_file, 'epub', outputfile=output_epub)
    except Exception as e:
        pass

def send_email_with_attachment(epub_file, config):
    """
    Send the EPUB file to the specified Kindle email address via SMTP.
    """
    # Create email
    msg = MIMEMultipart()
    msg['From'] = config['smtp_user']
    msg['To'] = config['kindle_email']
    msg['Subject'] = 'New EPUB for Your Kindle'

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
    except Exception as e:
        pass

def main():
    # Load config settings from config.json
    config = load_config('config.json')

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

if __name__ == "__main__":
    main()
