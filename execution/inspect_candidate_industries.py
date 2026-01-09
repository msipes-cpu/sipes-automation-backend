import pandas as pd

INPUT_FILE = "marketing/agency_owners_batch_2.csv"

def main():
    df = pd.read_csv(INPUT_FILE)
    
    # Normalize
    df['job_title'] = df['job_title'].astype(str).str.lower().fillna('')
    df['industry'] = df['industry'].astype(str).str.lower().fillna('')
    
    # Role Filter
    target_roles = ["owner", "president", "ceo", "founder", "partner", "principal", "chief executive"]
    role_mask = df['job_title'].apply(lambda x: any(r in x for r in target_roles))
    
    candidates = df[role_mask].copy()
    
    print(f"Total Candidates (Owners): {len(candidates)}")
    
    # Count industries
    print("\nTop 40 Industries of Candidates:")
    print(candidates['industry'].value_counts().head(40))

if __name__ == "__main__":
    main()
