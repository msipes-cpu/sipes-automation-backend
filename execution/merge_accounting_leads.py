import csv
import os
import sys

# Files to merge
file1 = "Accounting_High_Yield_20260111_2324.csv"
file2 = "Accounting_Recovery_Run_20260112_0653.csv"
output_file = "Accounting_Master_Combined_20260112.csv"

def read_csv(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

data1, folder1 = read_csv(file1)
data2, folder2 = read_csv(file2)

# Verify headers match (or close enough)
# "Source" might be missing in file1, so we allow that.
all_fields = folder2 if "Source" in folder2 else folder1
if "Source" not in all_fields:
    all_fields.append("Source") # Ensure it's there

combined_data = data1 + data2
unique_data = {}

# Dedup by Email just in case
for row in combined_data:
    email = row.get("Email")
    if email:
        unique_data[email] = row

final_rows = list(unique_data.values())

print(f"Merging {len(data1)} + {len(data2)} leads...")
print(f"Total Unique Leads: {len(final_rows)}")

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_fields)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"Written to {output_file}")
