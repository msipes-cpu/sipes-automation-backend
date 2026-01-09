import pandas as pd
import glob
import os
from datetime import datetime

def categorize_industry(industry):
    if not isinstance(industry, str):
        return "Other"
    
    ind_lower = industry.lower()
    
    # Manufacturing
    if any(x in ind_lower for x in ['manufacturing', 'industrial', 'automotive', 'machinery', 'textile', 'chemical', 'plastics', 'packaging']):
        return "Manufacturing"
    
    # Shipping (Prioritize over Logistics if specific)
    if any(x in ind_lower for x in ['maritime', 'freight', 'truck', 'aviation', 'delivery', 'shipping', 'transport', 'carrier', 'cargo', 'fleet']):
        # If it says "Transportation, Logistics" it's a bit ambiguous, but let's see.
        if "logistics" in ind_lower and "transportation" in ind_lower:
             return "Logistics" 
        return "Shipping"

    # Logistics
    if any(x in ind_lower for x in ['logistics', 'supply chain', 'warehouse', 'storage', 'distribution', 'fulfillment', '3pl', 'inventory']):
        return "Logistics"
        
    return "Other"

def main():
    print("🔄 Starting Consolidation & Re-Categorization...")
    
    # Read ALL verified leads files (old and new)
    files = glob.glob("marketing/leads_output/all_verified_leads_*.csv")
    if not files:
        print("⚠️ No all_verified_leads files found.")
        return

    print(f"📦 Found {len(files)} raw files. combining...")
    
    df_list = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df_list.append(df)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    if not df_list:
        return

    combined = pd.concat(df_list, ignore_index=True)
    before = len(combined)
    
    # Deduplicate
    combined.drop_duplicates(subset=['Email'], keep='last', inplace=True)
    after = len(combined)
    print(f"   Total rows: {before} -> Unique: {after}")
    
    # Re-Categorize
    print("   Re-applying Industry Categorization...")
    combined['Category'] = combined['Industry'].apply(categorize_industry)
    
    # Split
    shipping = combined[combined['Category'] == 'Shipping']
    logistics = combined[combined['Category'] == 'Logistics']
    manufacturing = combined[combined['Category'] == 'Manufacturing']
    other = combined[combined['Category'] == 'Other']
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("marketing/leads_output/consolidated", exist_ok=True)
    
    shipping_path = f"marketing/leads_output/consolidated/Shipping_Leads_Master_{timestamp}.csv"
    logistics_path = f"marketing/leads_output/consolidated/Logistics_Leads_Master_{timestamp}.csv"
    manufacturing_path = f"marketing/leads_output/consolidated/Manufacturing_Leads_Master_{timestamp}.csv"
    all_path = f"marketing/leads_output/consolidated/All_Leads_Master_{timestamp}.csv"
    
    shipping.to_csv(shipping_path, index=False)
    logistics.to_csv(logistics_path, index=False)
    manufacturing.to_csv(manufacturing_path, index=False)
    combined.to_csv(all_path, index=False)
    
    print("\n📊 Final Validated Counts:")
    print(f"Shipping: {len(shipping)} (Saved to {shipping_path})")
    print(f"Logistics: {len(logistics)} (Saved to {logistics_path})")
    print(f"Manufacturing: {len(manufacturing)} (Saved to {manufacturing_path})")
    print(f"Other: {len(other)}")
    print(f"Total Unique: {len(combined)}")

if __name__ == "__main__":
    main()
