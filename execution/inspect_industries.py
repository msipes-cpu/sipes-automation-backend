import csv
from collections import Counter

INPUT_FILE = "marketing/agency_owners_raw.csv"

def main():
    industries = Counter()
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ind = row.get("industry", "").strip()
            if ind:
                industries[ind] += 1
            else:
                industries["(Unknown)"] += 1
                
    print("Top 20 Industries found:")
    for ind, count in industries.most_common(20):
        print(f"{ind}: {count}")

if __name__ == "__main__":
    main()
