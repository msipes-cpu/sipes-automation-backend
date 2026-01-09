import csv

INPUT_FILE = "marketing/agency_owners_raw.csv"

def main():
    print("Inspecting 'Marketing & Advertising' rows...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        count = 0
        found = 0
        for row in reader:
            count += 1
            industry = row.get("industry", "").lower()
            
            if "marketing" in industry and "advertising" in industry:
                found += 1
                print(f"\n--- Row {count} ---")
                print(f"Name: {row.get('first_name')} {row.get('last_name')}")
                print(f"Role: {row.get('job_title')}")
                print(f"Company: {row.get('company_name')}")
                print(f"Industry: {row.get('industry')}")
                print(f"Desc: {row.get('company_description')[:100]}...")

    print(f"\nTotal 'Marketing & Advertising' rows: {found}")

if __name__ == "__main__":
    main()
