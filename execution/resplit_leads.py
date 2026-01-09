
import pandas as pd
import os
import glob

# Find the latest "all_verified_leads" file
list_of_files = glob.glob('marketing/leads_output/all_verified_leads_*.csv')
latest_file = max(list_of_files, key=os.path.getctime)
print(f"Propcessing file: {latest_file}")

df = pd.read_csv(latest_file)

def categorize_industry(industry):
    if not isinstance(industry, str):
        return "Other"
    
    ind_lower = industry.lower()
    
    # Manufacturing
    if any(x in ind_lower for x in ['manufacturing', 'industrial', 'automotive', 'machinery', 'textile', 'chemical', 'plastics', 'packaging']):
        return "Manufacturing"
    
    # Shipping (Prioritize over Logistics if specific)
    if any(x in ind_lower for x in ['maritime', 'freight', 'truck', 'aviation', 'delivery', 'shipping', 'transport']):
        # If it says "Transportation, Logistics" it's a bit ambiguous, but let's see.
        # "Maritime Transportation" -> Shipping
        # "Truck Transportation" -> Shipping
        # "Transportation, Logistics, Supply Chain and Storage" -> Logistics (usually broader)
        if "logistics" in ind_lower and "transportation" in ind_lower:
             return "Logistics" # Keep the big category as Logistics
        return "Shipping"

    # Logistics
    if any(x in ind_lower for x in ['logistics', 'supply chain', 'warehouse', 'storage', 'distribution']):
        return "Logistics"
        
    return "Other"

# Re-apply categorization
df['Category'] = df['Industry'].apply(categorize_industry)

# Split
shipping = df[df['Category'] == 'Shipping']
logistics = df[df['Category'] == 'Logistics']
manufacturing = df[df['Category'] == 'Manufacturing']

# Save with same timestamp as input to avoid confusion, or new one. Let's use new one.
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

shipping_file = f"marketing/leads_output/Shipping_Leads_{timestamp}.csv"
logistics_file = f"marketing/leads_output/Logistics_Leads_{timestamp}.csv"
manufacturing_file = f"marketing/leads_output/Manufacturing_Leads_{timestamp}.csv"
all_file = f"marketing/leads_output/all_verified_leads_categorized_{timestamp}.csv"

shipping.to_csv(shipping_file, index=False)
logistics.to_csv(logistics_file, index=False)
manufacturing.to_csv(manufacturing_file, index=False)
df.to_csv(all_file, index=False)

print(f"Summary:")
print(f"Shipping: {len(shipping)}")
print(f"Logistics: {len(logistics)}")
print(f"Manufacturing: {len(manufacturing)}")
print(f"Total: {len(df)}")
