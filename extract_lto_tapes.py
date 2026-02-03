import csv
import sys
import os
import argparse
import xml.etree.ElementTree as ET

def parse_xml_media(xml_file_path):
    """
    Parses an XML file and extracts media filenames.
    Assumes media file names are located in //file/name.
    """
    media_names = set()
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        # Find all <file> elements and their <name> children
        for file_elem in root.iter('file'):
            name_elem = file_elem.find('name')
            if name_elem is not None and name_elem.text:
                full_name = name_elem.text.strip()
                # Store only the base name (ignore extension)
                base_name = os.path.splitext(full_name)[0]
                media_names.add(base_name)
    except Exception as e:
        print(f"Error parsing XML file: {e}")
        return set()
    return media_names


def extract_lto_tapes(csv_file_path, xml_media_names=None):
    """
    Reads a CSV file.
    If xml_media_names is provided, returns LTO tapes that contain any of the media names.
    If not, returns all unique LTO tapes found in the CSV.
    
    Args:
        csv_file_path (str): Path to the CSV file.
        xml_media_names (set, optional): Set of media filenames to search for.
        
    Returns:
        dict: A dictionary where key is LTO tape name and value is a list of file paths.
    """
    tape_files_map = {}
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8', errors='replace') as csvfile:
            # Detect whether the file has a header
            sample = csvfile.read(1024)
            csvfile.seek(0)
            has_header = csv.Sniffer().has_header(sample)
            
            reader = csv.DictReader(csvfile) if has_header else csv.reader(csvfile)
            
            # If we are searching for specific media, we need to look at 'Media' (LTO) AND 'Name' (Filename)
            # Based on previous `head` output:
            # Path,Media,Type,Name,...
            # Path is index 0, Media is index 1, Name is index 3
            
            if has_header:
                for row in reader:
                    tape = row.get('Media', '').strip()
                    filename = row.get('Name', '').strip()
                    file_path = row.get('Path', '').strip()
                    
                    if not tape:
                        continue
                        
                    if xml_media_names:
                        # Check if base name matches any in the XML list
                        base_name = os.path.splitext(filename)[0]
                        if base_name in xml_media_names:
                            if tape not in tape_files_map:
                                tape_files_map[tape] = []
                            tape_files_map[tape].append(file_path)
                    else:
                         if tape not in tape_files_map:
                                tape_files_map[tape] = []
                         # If no XML filter, we essentially just want the list of tapes, 
                         # but we'll store paths anyway for consistency if needed, 
                         # or just store empty list if paths aren't the primary goal without filter.
                         # For now, let's just store the paths to be safe.
                         tape_files_map[tape].append(file_path)
            else:
                 # Fallback if no header
                 reader = csv.reader(csvfile)
                 first_row = next(reader, None)
                 
                 # Logic for manual column mapping if header is missing but data structure is known
                 # 0: Path, 1: Media, 3: Name
                 
                 if first_row:
                     # Check if first row is actually a header that wasn't detected
                     if first_row[1] == 'Media':
                         pass # Skip, it's a header
                     else:
                        # Process first row
                        if len(first_row) > 3:
                            tape = first_row[1].strip()
                            filename = first_row[3].strip()
                            file_path = first_row[0].strip()
                            if tape:
                                if xml_media_names:
                                    base_name = os.path.splitext(filename)[0]
                                    if base_name in xml_media_names:
                                        if tape not in tape_files_map:
                                            tape_files_map[tape] = []
                                        tape_files_map[tape].append(file_path)
                                else:
                                     if tape not in tape_files_map:
                                        tape_files_map[tape] = []
                                     tape_files_map[tape].append(file_path)

                 for row in reader:
                     if len(row) > 3:
                         tape = row[1].strip()
                         filename = row[3].strip()
                         file_path = row[0].strip()
                         if tape:
                              if xml_media_names:
                                 base_name = os.path.splitext(filename)[0]
                                 if base_name in xml_media_names:
                                     if tape not in tape_files_map:
                                        tape_files_map[tape] = []
                                     tape_files_map[tape].append(file_path)
                              else:
                                 if tape not in tape_files_map:
                                    tape_files_map[tape] = []
                                 tape_files_map[tape].append(file_path)

    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return {}
        
    return tape_files_map

def main():
    parser = argparse.ArgumentParser(description="Extract LTO tapes from CSV, optionally filtering by media from an XML file.")
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("--xml", help="Path to the XML file containing media list", default=None)
    
    args = parser.parse_args()
    
    csv_file = args.csv_file
    xml_file = args.xml
    
    if not os.path.isfile(csv_file):
         print(f"Error: '{csv_file}' is not a valid file.")
         sys.exit(1)

    xml_media_names = None
    if xml_file:
        if not os.path.isfile(xml_file):
            print(f"Error: '{xml_file}' is not a valid file.")
            sys.exit(1)
        print(f"Parsing XML file: {xml_file}...")
        xml_media_names = parse_xml_media(xml_file)
        
        print(f"Found {len(xml_media_names)} unique media items in XML:")
        for name in sorted(xml_media_names):
            print(f" - {name}")
        print("-" * 30)

    print(f"Scanning CSV file: {csv_file}...")
    tape_files_map = extract_lto_tapes(csv_file, xml_media_names)
    
    if tape_files_map:
        if xml_file:
            print("\nLTO Tapes containing the requested media:")
        else:
             print("\nLTO Tapes found in CSV:")
             
        for tape in sorted(tape_files_map.keys()):
            print(tape)
        
        # Only print paths if XML filter was used, to match previous behavior/requirement
        if xml_file:
             print("\nFull paths of matched media:")
             for tape, paths in tape_files_map.items():
                 for path in paths:
                     print(path)

    else:
        print("No matching LTO tapes found.")


if __name__ == "__main__":
    main()
