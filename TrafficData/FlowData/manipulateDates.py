from pathlib import Path
from datetime import datetime
import csv

def update_dates_in_csv(file_path):
    # Backup the original file
    backup_path = file_path.with_suffix('.bak')
    file_path.rename(backup_path)
    
    with open(backup_path, mode='r', newline='') as infile, \
         open(file_path, mode='w', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            if len(row) == 3:  # Ensure the row has at least 4 columns
                try:
                    # Original date string from column 3 (index 3)
                    original_date_str = row[3]
                    
                    # Parse the original date string
                    date1 = datetime.strptime(original_date_str, "%m/%d/%Y")
                    
                    # Format the date as YYYY-MM-DD
                    new_date_str = date1.strftime("%Y-%m-%d")
                    
                    # Update the date in the row
                    row[3] = new_date_str
                    
                except ValueError:
                    # Handle the case where the date string does not match the format
                    print(f"Date format error for: {row[3]}")
            
            # Write the updated row to the new file
            writer.writerow(row)

# Example usage
tcdata = Path('ChicagoADT2006.csv')
if tcdata.exists():
    print("CHECK!")
    update_dates_in_csv(tcdata)
else:
    print("FAIL!")
