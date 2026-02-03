import argparse
import sys
import os
import shutil
import time
from extract_lto_tapes import extract_lto_tapes, parse_xml_media

def restore_media(csv_file, xml_file, destination):
    """
    Coordinates the restoration of media from LTO tapes.
    """
    if not os.path.exists(destination):
        try:
            os.makedirs(destination)
        except OSError as e:
            print(f"Error creating destination directory: {e}")
            return

    print("Analyzing requirements...")
    if xml_file:
         print(f"Parsing XML file: {xml_file}...")
         xml_media_names = parse_xml_media(xml_file)
         print(f"Found {len(xml_media_names)} unique media items in XML.")
         tape_files_map = extract_lto_tapes(csv_file, xml_media_names)
    else:
         print("No XML file provided. Scanning entire CSV (this might restore A LOT of files)...")
         # If no XML is provided, we restore everything? Or should we warn?
         # The prompt implies getting the list "found in the CSV" which usually means filtered by XML
         # based on context, but let's handle the extraction call.
         tape_files_map = extract_lto_tapes(csv_file)
    
    if not tape_files_map:
        print("No files to restore found.")
        return

    # Analyze found files for extensions and potential duplicates
    all_extensions = set()
    base_name_extensions = {} # base_name -> set of extensions found

    for tape, files in tape_files_map.items():
        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            ext = os.path.splitext(f)[1].lower() # Normalize ext
            all_extensions.add(ext)
            
            if base not in base_name_extensions:
                base_name_extensions[base] = set()
            base_name_extensions[base].add(ext)

    # Check for duplicates (same name, diff ext)
    duplicates_found = False
    for base, exts in base_name_extensions.items():
        if len(exts) > 1:
            duplicates_found = True
            break
            
    print("\n" + "="*40)
    print("Media Analysis")
    print("="*40)
    print(f"File extensions found: {', '.join(sorted(all_extensions))}")
    if duplicates_found:
        print("WARNING: Found files with the same name but different extensions!")
        # Optional: Print some examples?
        count = 0
        for base, exts in base_name_extensions.items():
             if len(exts) > 1:
                 print(f" - {base}: {', '.join(exts)}")
                 count += 1
                 if count >= 3:
                     print("   ...")
                     break
    
    # Prompt user for preference
    print("\nYou can choose to restore only files with a specific extension.")
    preferred_ext = input("Enter preferred extension to restore (e.g. .mxf) or press ENTER for ALL: ").strip().lower()
    
    if preferred_ext:
        if not preferred_ext.startswith('.'):
            preferred_ext = '.' + preferred_ext
            
        print(f"Filtering for extension: {preferred_ext}")
        
        # Filter tape_files_map
        new_map = {}
        for tape, files in tape_files_map.items():
            filtered = [f for f in files if f.lower().endswith(preferred_ext)]
            if filtered:
                new_map[tape] = filtered
        
        tape_files_map = new_map
        
        if not tape_files_map:
             print(f"No files found matching extension '{preferred_ext}'. Restoration aborted.")
             return

    sorted_tapes = sorted(tape_files_map.keys())
    total_tapes = len(sorted_tapes)
    print(f"\nRestoration Plan:")
    print(f"Found files on {total_tapes} tapes.")
    for tape in sorted_tapes:
        print(f" - {tape}: {len(tape_files_map[tape])} files")
    
    print("\nStarting restoration process...")
    
    for i, tape in enumerate(sorted_tapes):
        files_to_copy = tape_files_map[tape]
        print("\n" + "="*60)
        print(f"Tape {i+1} of {total_tapes}: {tape}")
        print("="*60)
        
        while True:
            input(f"\n>>> Please MOUNT tape '{tape}' and press ENTER when ready <<<")
            
            # Verify if tape is mounted by checking if the first file exists
            # Note: This checks the absolute path from the CSV.
            # If the CSV paths are like /Volumes/TapeName/..., this works if mounted there.
            
            missing_files = []
            accessible_files = []
            
            print("Verifying tape access...")
            # We assume if we can access the first file, the tape is likely mounted.
            # However, LTO file systems might show files even if offline? 
            # Usually strict existence check is good enough for "mounted at expected path".
            
            all_accessible = True
            # Quick check of the first file to validate mount point quickly
            if files_to_copy:
                first_file = files_to_copy[0]
                if not os.path.exists(first_file):
                     print(f"Warning: Cannot find expected file: {first_file}")
                     print(f"Is tape '{tape}' mounted at the correct location?")
                     retry = input("Retry (r) or Skip this tape (s)? [r/s]: ").lower()
                     if retry == 's':
                         break
                     else:
                         continue # Retry loop
            
            # If we pass the basic check, we assume we can proceed or at least try.
            break
        
        # Proceed with copy
        print(f"\nCopying {len(files_to_copy)} files from {tape} to {destination}...")
        
        success_count = 0
        fail_count = 0
        
        for file_path in files_to_copy:
            try:
                if os.path.exists(file_path):
                    # Create destination structure? Or flat copy?
                    # Request was "copy the files... to a desired destination".
                    # Let's preserve filename but maybe not full tree unless collision.
                    # Simple approach: Copy to flat destination or maintain relative?
                    # Given typical workflows, flat or protecting name collisions is best.
                    # Let's use basename for now, but handle collisions?
                    # Or better, just flat copy.
                    
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(destination, filename)
                    
                    # Handle collisions
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        dest_path = os.path.join(destination, f"{base}_{int(time.time())}{ext}")
                    
                    print(f"Copying: {filename}")
                    shutil.copy2(file_path, dest_path)
                    success_count += 1
                else:
                    print(f"Error: File not found (skipped): {file_path}")
                    fail_count += 1
            except Exception as e:
                print(f"Failed to copy {file_path}: {e}")
                fail_count += 1
                
        print(f"\nTape '{tape}' finished.")
        print(f"Copied: {success_count}, Failed: {fail_count}")
        
        if i < total_tapes - 1:
            input(f"\n>>> Please EJECT tape '{tape}' and press ENTER to continue <<<")
    
    print("\nAll restoration tasks completed.")

def main():
    parser = argparse.ArgumentParser(description="Restore media from LTO tapes interactively.")
    parser.add_argument("csv_file", help="Path to the master CSV file")
    parser.add_argument("--xml", help="Path to the XML file requiring media", default=None)
    parser.add_argument("--dest", help="Destination folder for restored files", required=True)
    
    args = parser.parse_args()
    
    restore_media(args.csv_file, args.xml, args.dest)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRestoration cancelled by user.")
        sys.exit(0)
