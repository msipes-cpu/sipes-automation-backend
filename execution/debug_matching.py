import csv

INPUT_FILE = "marketing/agency_owners_raw.csv"

def main():
    print("Debugging first 50 rows...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        count = 0
        matches = 0
        for row in reader:
            count += 1
            if count > 100:
                break
            
            industry = row.get("industry", "").lower()
            role = row.get("job_title", "").lower()
            
            # Target roles
            target_roles = ["owner", "president", "ceo", "founder", "partner", "principal", "chief executive"]
            if not any(r in role for r in target_roles):
                # print(f"Row {count}: Failed Role ({role})")
                continue
            
            # Negative Role
            bad_roles = ["product owner", "project owner", "process owner", "business owner analyst", "franchise owner", "sales development"]
            if any(br in role for br in bad_roles):
                print(f"Row {count}: Failed Negative Role ({role})")
                continue
                
            # Negative Industry
            company_desc = row.get("company_description", "").lower()
            keywords = row.get("keywords", "").lower()
            combined_text = f"{company_desc} {industry} {keywords} {row.get('company_name', '').lower()}"
            
            negative_signals = [
                "insurance", "real estate", "home care", "healthcare", "senior care", 
                "fitness", "gym", "dental", "medical", "construction", "cleaning", 
                "staffing", "recruiting", "mortgage", "bank", "financial", "investment",
                "pest control", "plumbing", "hvac", "roofing", "auto", "car",
                "trucking", "logistics", "shipping", "manufacturing", "dairy", "food",
                "restaurant", "franchise", "therapy", "counseling", "nursing", "pharmacy",
                "wholesale", "retail"
            ]
            
            bad_signal = None
            for ns in negative_signals:
                if ns in combined_text:
                    bad_signal = ns
                    break
            
            if bad_signal:
                print(f"Row {count}: Failed Negative Signal '{bad_signal}' (Industry: {industry})")
                continue
                
            # Positive Signals
            marketing_signals = [
                "digital marketing", "advertising agency", "creative agency", "media agency", 
                "pr agency", "public relations", "seo agency", "web design",
                "branding", "content marketing", "social media", 
                "marketing strategy", "lead generation", "marketing & advertising",
                "advertising services"
            ]
            
            is_marketing = False
            allowed_industries = ["marketing & advertising", "marketing and advertising", "online media", "graphic design", "public relations and communications"]
            
            if any(ai in industry for ai in allowed_industries):
                is_marketing = True
            
            print(f"Row {count}: Passed Negatives. Industry: {industry}. Role: {role}. Is Marketing? {is_marketing}")
            matches += 1

if __name__ == "__main__":
    main()
