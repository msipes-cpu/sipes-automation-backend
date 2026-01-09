import csv
import os

file_path = 'marketing/first_five_tracking.csv'
temp_file_path = 'marketing/first_five_tracking_temp.csv'

# The 20 names we listed to the user
target_names = [
    "Herbert Williams", "Larry Jenkins", "Chris Bross", "Kara Thomas", "John King",
    "Christine Sonnenberg", "Kim Coates", "Peter Markov", "Michael Peterson", "Alice Olivas",
    "Elijah Perry", "Neil Burtt", "Ann Milan", "Istehsan Shah", "Breanne Swarts",
    "Ali Khan", "Lauren Rubenstein", "Levi Kepler", "Kristy Boulos", "Julie Morris"
]

updated_count = 0

with open(file_path, 'r', newline='', encoding='utf-8') as infile, \
     open(temp_file_path, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        if row['Name'] in target_names:
            row['Contacted?'] = 'Yes'
            updated_count += 1
        writer.writerow(row)

os.replace(temp_file_path, file_path)
print(f"Updated {updated_count} records.")
