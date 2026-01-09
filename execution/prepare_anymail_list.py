
import csv
import os

OUTPUT_FILE = "marketing/companies_temp.csv"

# Data gathered from manual search
DATA = [
    {"Company": "Belkins", "Domain": "belkins.io", "First Name": "Vladislav", "Last Name": "Podolyako"},
    {"Company": "CIENCE", "Domain": "cience.com", "First Name": "John", "Last Name": "Girard"},
    {"Company": "Callbox", "Domain": "callboxinc.com", "First Name": "Rom", "Last Name": "Agustin"},
    {"Company": "Martal Group", "Domain": "martal.ca", "First Name": "Vito", "Last Name": "Vishnepolsky"},
    {"Company": "Smith.ai", "Domain": "smith.ai", "First Name": "Aaron", "Last Name": "Lee"},
    {"Company": "Leadium", "Domain": "leadium.com", "First Name": "Kevin", "Last Name": "Warner"},
    {"Company": "SalesRoads", "Domain": "salesroads.com", "First Name": "David", "Last Name": "Kreiger"},
    {"Company": "Pearl Lemon Leads", "Domain": "pearllemonleads.com", "First Name": "Deepak", "Last Name": "Shukla"},
    {"Company": "LeadGenius", "Domain": "leadgenius.com", "First Name": "Mark", "Last Name": "Godley"},
    # {"Company": "Salespanel", "Domain": "salespanel.io", "First Name": "", "Last Name": ""}, # CEO unclear
    {"Company": "SalesBread", "Domain": "salesbread.com", "First Name": "Jack", "Last Name": "Reamer"},
    {"Company": "SalesPro Leads", "Domain": "salesproleads.com", "First Name": "Tom", "Last Name": "Cherry"},
    {"Company": "MemoryBlue", "Domain": "memoryblue.com", "First Name": "Chris", "Last Name": "Corcoran"},
    {"Company": "Televerde", "Domain": "televerde.com", "First Name": "Vince", "Last Name": "Barsolo"},
    {"Company": "SalesAR", "Domain": "salesar.io", "First Name": "Roman", "Last Name": "Shvets"},
    {"Company": "Inbox Insights", "Domain": "inboxinsights.com", "First Name": "Jamie", "Last Name": "Hendrie"},
    {"Company": "WebFX", "Domain": "webfx.com", "First Name": "William", "Last Name": "Craig"},
    {"Company": "LevelUp Leads", "Domain": "levelupleads.com", "First Name": "John", "Last Name": "Karsant"},
    {"Company": "RevBoss", "Domain": "revboss.com", "First Name": "Eric", "Last Name": "Boggs"},
    {"Company": "UnboundB2B", "Domain": "unboundb2b.com", "First Name": "Rameshwar", "Last Name": "Sahu"},
    {"Company": "Dealfront", "Domain": "dealfront.com", "First Name": "Kevin", "Last Name": "McIntyre"},
    {"Company": "Snov.io", "Domain": "snov.io", "First Name": "Oleksii", "Last Name": "Kratko"},
    {"Company": "Lusha", "Domain": "lusha.com", "First Name": "Yoni", "Last Name": "Tserruya"},
    {"Company": "Cognism", "Domain": "cognism.com", "First Name": "Pete", "Last Name": "Daffern"},
    {"Company": "Kaspr", "Domain": "kaspr.io", "First Name": "Allan", "Last Name": "Benguigui"},
    {"Company": "UpLead", "Domain": "uplead.com", "First Name": "Will", "Last Name": "Cannon"},
    {"Company": "Shortlist Marketing", "Domain": "shortlistmarketing.co.uk", "First Name": "Paul", "Last Name": "Breloff"},
    {"Company": "Operatix", "Domain": "operatix.net", "First Name": "Aurelien", "Last Name": "Mottier"}
]

def main():
    print(f"Generating {OUTPUT_FILE} with {len(DATA)} companies...")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Company", "Domain", "First Name", "Last Name"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(DATA)
        
    print("Done.")

if __name__ == "__main__":
    main()
