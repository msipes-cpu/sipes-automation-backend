import os

COUNTER_FILE = "proposal_counter.txt"

def get_next_proposal_number():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1000") # Start at 1000
    
    with open(COUNTER_FILE, "r") as f:
        try:
            current = int(f.read().strip())
        except ValueError:
            current = 1000
            
    next_num = current + 1
    
    with open(COUNTER_FILE, "w") as f:
        f.write(str(next_num))
        
    # Format J#####P (J01000P)
    # User said "starting with J01000P". Let's assume 5 digits padding?
    # "J#####P". "start with J01000P".
    # If standard is 5 digits: J01000P.
    return f"J{current:05d}P"

if __name__ == "__main__":
    print(get_next_proposal_number())
