# WGM
# A simple script to extract or merge PDF files using PyPDF2

import os
from PyPDF2 import PdfReader, PdfWriter

def parse_page_input(pages_input, max_pages):
    """
    Parses a page input string (e.g., "1,3,5-7") into a list of 0-indexed pages.
    Validates page numbers against max_pages.
    """
    pages_to_process = []
    
    for part in pages_input.split(","):
        part = part.strip()
        if not part:
            continue
            
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
            except ValueError:
                raise ValueError(f"Invalid range '{part}'. Must be like '5-7'.")
                
            if start < 1 or end > max_pages or start > end:
                raise ValueError(f"Page range '{part}' is out of range (1-{max_pages}).")
            
            # Add 0-indexed pages
            pages_to_process.extend(range(start - 1, end))
        else:
            try:
                p = int(part)
            except ValueError:
                raise ValueError(f"Invalid page number '{part}'. Must be an integer.")
            
            if p < 1 or p > max_pages:
                raise ValueError(f"Page number {p} is out of range (1-{max_pages}).")
            
            # Add 0-indexed page
            pages_to_process.append(p - 1)
            
    # Remove duplicates and sort, though 0-indexing is the key
    return sorted(list(set(pages_to_process)))


def clean_path(path):
    """Removes surrounding quotes and whitespace from a file path."""
    return path.strip().strip('"').strip("'")

def do_extraction():
    """Handles the logic for extracting pages from a single PDF."""
    try:
        pdf_path = clean_path(input("Enter the path to your PDF file: "))
        
        if not os.path.exists(pdf_path):
            print(f"Error: The file '{pdf_path}' does not exist.")
            return

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"File has {total_pages} pages.")

        pages_input = input(f"Enter page numbers to extract (e.g., 1,3,5-{total_pages}): ").strip()
        
        # Parse and validate pages
        page_indices = parse_page_input(pages_input, total_pages)
        
        if not page_indices:
            print("No valid pages selected.")
            return

        writer = PdfWriter()
        for p_index in page_indices:
            writer.add_page(reader.pages[p_index])

        # Output filename
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_extracted.pdf"

        with open(output_path, "wb") as out_file:
            writer.write(out_file)

        # Show 1-indexed pages in success message
        print(f"\nSuccessfully extracted pages {[p + 1 for p in page_indices]} -> '{output_path}'")

    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"\nAn error occurred: {e}")

def do_merging():
    """Handles the logic for merging multiple PDFs."""
    
    writer = PdfWriter()
    files_merged = 0
    
    print("\n--- PDF Merge Mode ---")
    print("Enter paths to PDFs one by one. Press ENTER on an empty line to finish.")

    try:
        while True:
            pdf_path = clean_path(input(f"Path to PDF #{files_merged + 1}: "))
            
            if not pdf_path:
                if files_merged == 0:
                    print("No files entered. Exiting merge mode.")
                    return
                else:
                    break # User is done adding files

            if not os.path.exists(pdf_path):
                print(f"Warning: File '{pdf_path}' not found. Skipping.")
                continue

            try:
                reader = PdfReader(pdf_path)
                total_pages = len(reader.pages)
                print(f"  > File '{os.path.basename(pdf_path)}' has {total_pages} pages.")
                
                page_indices = []

                # Ask user for all or specific pages
                while True:
                    choice = input("  > Merge (all) pages or (specific) pages? [all/specific]: ").strip().lower()
                    
                    if choice == 'all':
                        page_indices = list(range(total_pages)) # All 0-indexed pages
                        break
                    elif choice == 'specific':
                        pages_input = input(f"  > Enter page numbers (e.g., 1,3,5-{total_pages}): ").strip()
                        page_indices = parse_page_input(pages_input, total_pages)
                        break
                    else:
                        print("  > Invalid choice. Please enter 'all' or 'specific'.")
                
                # Add the selected pages to the writer
                for p_index in page_indices:
                    writer.add_page(reader.pages[p_index])
                
                print(f"  > Added {[p + 1 for p in page_indices]} from this file.")
                files_merged += 1

            except Exception as e:
                print(f"  > Error reading file '{pdf_path}': {e}. Skipping this file.")

        # After loop, save the merged file
        if files_merged > 0:
            output_path = input("\nEnter name for the final merged file (e.g., merged.pdf): ").strip()
            if not output_path.lower().endswith('.pdf'):
                output_path += ".pdf"

            with open(output_path, "wb") as out_file:
                writer.write(out_file)
            
            print(f"\nSuccessfully merged {files_merged} files -> '{output_path}'")

    except (ValueError, Exception) as e:
        print(f"\nAn error occurred during merging: {e}")


if __name__ == "__main__":
    print("--- PDF Tool ---")
    while True:
        mode = input("Do you want to (1) Extract pages or (2) Merge PDFs? [1/2]: ").strip()
        
        if mode == '1':
            do_extraction()
            break
        elif mode == '2':
            do_merging()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")