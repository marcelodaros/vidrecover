
import csv
import os
import sys

def debug_csv_parsing(csv_file_path):
    print(f"Debugging CSV: {csv_file_path}")
    
    xml_media_names = {"A_0045C016_250603_101833_p1C6J"} # The one we know is in there
    tape_files_map = {}
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8', errors='replace') as csvfile:
            # Sniffer logic from extract_lto_tapes.py
            sample = csvfile.read(1024)
            csvfile.seek(0)
            has_header = False
            try:
                has_header = csv.Sniffer().has_header(sample)
            except Exception as e:
                print(f"Sniffer error: {e}")
            
            print(f"Sniffer detected header: {has_header}")
            
            reader = csv.DictReader(csvfile) if has_header else csv.reader(csvfile)
            
            if has_header:
                print("Using DictReader...")
                count = 0
                for row in reader:
                    # Print first few rows to see what Keys we have
                    if count < 1:
                        print(f"Row {count} keys: {[repr(k) for k in row.keys()]}")
                        print(f"Row {count} 'Path': '{row.get('Path', 'MISSING')}'")
                        print(f"Row {count} 'Name': '{row.get('Name', '')}'")
                    
                    filename = row.get('Name', '').strip()
                    file_path = row.get('Path', '').strip()
                    
                    if not file_path:
                         if count < 5: print(f"WARNING: Empty path at row {count}")
                    
                    # Check our target
                    base = os.path.splitext(filename)[0]
                    if base in xml_media_names:
                        print(f"MATCH FOUND via DictReader! File: {filename}")
                        print(f"   Path: {file_path}")
                    
                    count += 1
            else:
                 print("Using csv.reader (fallback)...")
                 # Fallback logic
                 reader = csv.reader(csvfile)
                 first_row = next(reader, None)
                 print(f"First row: {first_row}")
                 
                 # ... simplified loop
                 for row in reader:
                     if len(row) > 3:
                         filename = row[3].strip()
                         csv_media = row[1].strip()
                         # Check target
                         base = os.path.splitext(filename)[0]
                         if base in xml_media_names:
                             print(f"MATCH FOUND via csv.reader! File: {filename}")
                             
    except Exception as e:
        print(f"Error: {e}")

debug_csv_parsing("2026-02-03_1729_WOLVES.CSV")
