import pypandoc
import os

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
        print(f"Converted {md_file} to {output_epub}")
    except Exception as e:
        print(f"Error converting {md_file} to EPUB: {e}")

def main():
    # Define the directory where markdown files are located
    md_directory = "."

    # Define output directory for EPUB files
    output_directory = "."
    os.makedirs(output_directory, exist_ok=True)

    # Get all markdown files in the directory
    md_files = get_md_files_in_directory(md_directory)

    # Convert each markdown file to EPUB
    for md_file in md_files:
        output_epub = os.path.join(output_directory, os.path.basename(md_file).replace(".md", ".epub"))
        convert_md_to_epub(md_file, output_epub)

if __name__ == "__main__":
    main()
