import os
import csv
from datetime import datetime

def scan_directories(directories, extensions, csv_path):
    """
    Scan given directories for files with specified extensions and save info to CSV.

    :param directories: List of directory paths to scan.
    :param extensions: Set of file extensions to include (e.g. {'.pdf', '.docx'}).
    :param csv_path: Path to output CSV file.
    :return: Number of files scanned.
    """
    file_records = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    full_path = os.path.join(root, file)
                    mod_time = os.path.getmtime(full_path)
                    mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    file_records.append([file, full_path, ext, mod_time_str])

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'FullPath', 'Extension', 'ModifiedTime'])
        writer.writerows(file_records)

    return len(file_records)

if __name__ == "__main__":
    # Example directories to scan - adjust as needed
    home = os.path.expanduser('~')
    system_drive = os.environ.get('SystemDrive', 'C:')
    directories_to_scan = [
    os.path.join(home, 'Documents'),
    os.path.join(home, 'Desktop'),
    os.path.join(home, 'Videos'),
    os.path.join(home, 'Pictures'),
    os.path.join(home, 'Downloads'),
    os.path.join(home, 'Music'),
    os.path.join(system_drive, 'Program Files'),
    os.path.join(system_drive, 'Program Files (x86)'),
    system_drive + '\\',  # Root of the system drive (C:\)
]
    # File types to track
    file_types = {'.pdf', '.docx', '.mp4'}

    # Path to save the CSV file
    output_csv = os.path.join(home, 'file_index.csv')

    # Run the scan
    num_files_scanned = scan_directories(directories_to_scan, file_types, output_csv)
    print(f"Scanned {num_files_scanned} files and saved to {output_csv}")

    # Optional: Uncomment below to update periodically every N seconds (e.g., 1 hour)
    # while True:
    #     num_files_scanned = scan_directories(directories_to_scan, file_types, output_csv)
    #     print(f"Scanned {num_files_scanned} files and saved to {output_csv}")
    #     time.sleep(3600)  # sleep for 1 hour
