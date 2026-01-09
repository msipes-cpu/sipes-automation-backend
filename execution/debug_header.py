import csv

INPUT_FILE = "marketing/agency_owners_raw.csv"

def main():
    print("Inspecting Row 166...")
    with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        count = 0
        for row in reader:
            count += 1
            if count == 166:
                print(f"Row {count} Found!")
                print(f"Company: {row.get('company_name')}")
                print(f"Name: {row.get('first_name')} {row.get('last_name')}")
                print(f"LinkedIn Key 'linkedin': '{row.get('linkedin')}'")
                print(f"LinkedIn Key 'company_linkedin': '{row.get('company_linkedin')}'")
                print("--- Keys ---")
                print(list(row.keys()))
                break

if __name__ == "__main__":
    main()
