
import xml.etree.ElementTree as ET
import os

def parse_xml_media_repro(xml_file_path):
    print(f"Parsing: {xml_file_path}")
    media_names = set()
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        count = 0
        slug_count = 0
        # This is the current logic in extract_lto_tapes.py
        for file_elem in root.iter('file'):
            name_elem = file_elem.find('name')
            if name_elem is not None and name_elem.text:
                full_name = name_elem.text.strip()
                if full_name == "Slug":
                    slug_count += 1
                base_name = os.path.splitext(full_name)[0]
                media_names.add(base_name)
                count += 1
        
        print(f"Total <file> elements processed: {count}")
        print(f"Total 'Slug' names found: {slug_count}")
        print(f"Unique media names found: {len(media_names)}")
        print("Sample names:", list(media_names)[:5])

        # New logic proposal check
        print("\n--- Testing Clipitem Parsing ---")
        clip_names = set()
        for clip_elem in root.iter('clipitem'):
             name_elem = clip_elem.find('name')
             if name_elem is not None and name_elem.text:
                 val = name_elem.text.strip()
                 # exclude basic names if necessary
                 clip_names.add(val)
        
        print(f"Unique clipitem names found: {len(clip_names)}")
        print("Sample clipitem names:", list(clip_names)[:5])

    except Exception as e:
        print(f"Error: {e}")

parse_xml_media_repro("wolves_reel01_20260203.xml")
