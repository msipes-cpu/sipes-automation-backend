import json
import os
import subprocess
import sys
import argparse

CONFIG_PATH = "config/clients.json"
ORCHESTRATOR_SCRIPT = "execution/orchestrate_leads.py"

def load_config(path):
    """Loads the client configuration from JSON."""
    if not os.path.exists(path):
        print(f"❌ Config file not found: {path}")
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse config file: {e}")
        return []

def run_command(command):
    """Run a shell command and print output."""
    print(f"Executing: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            
    return process.poll()

def main():
    parser = argparse.ArgumentParser(description="Multi-Tenant Master Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--client", help="Run for a specific client_id only")
    args = parser.parse_args()

    print("🚀 Starting Multi-Tenant Orchestration...")
    
    clients = load_config(CONFIG_PATH)
    if not clients:
        print("⚠️ No clients found in config.")
        return

    for client in clients:
        client_id = client.get("client_id")
        client_name = client.get("client_name")

        if args.client and args.client != client_id:
            continue

        print(f"\n👉 Processing Client: {client_name} ({client_id})")
        
        if "lead_orchestration" not in client.get("enabled_automations", []):
            print(f"⏩ Skipping 'lead_orchestration' for {client_name} (Not Enabled)")
            continue

        cmd_parts = [f"python3 {ORCHESTRATOR_SCRIPT}"]
        
        # Output base name unique to client
        output_base = f"leads_{client_id}"
        cmd_parts.append(f"--output_base {output_base}")

        # Isolation: Dedicated output directory
        client_output_dir = f".tmp/{client_id}"
        cmd_parts.append(f"--output_dir {client_output_dir}")

        if "job_titles" in client: # Note: config key was target_job_titles, ensuring mapping
             pass # Logic handled below

        if "target_job_titles" in client:
            titles = " ".join([f'"{t}"' for t in client["target_job_titles"]])
            cmd_parts.append(f"--job_titles {titles}")
        
        if "target_locations" in client:
            locs = " ".join([f'"{l}"' for l in client["target_locations"]])
            cmd_parts.append(f"--locations {locs}")
            
        if "target_industries" in client:
            inds = " ".join([f'"{i}"' for i in client["target_industries"]])
            cmd_parts.append(f"--industries {inds}")

        if "lead_limit" in client:
            cmd_parts.append(f"--limit {client['lead_limit']}")
            
        if "spreadsheet_id" in client and client["spreadsheet_id"]:
            cmd_parts.append(f"--spreadsheet_id {client['spreadsheet_id']}")
            
        # Add other client specific env vars or args as needed
        # For now, we assume orchestrator handles what it needs.
        # If API keys need to be passed as env vars:
        env_vars = os.environ.copy()
        if "instantly_api_key" in client:
            env_vars["INSTANTLY_API_KEY"] = client["instantly_api_key"]
            
        full_command = " ".join(cmd_parts)
        
        if args.dry_run:
            print(f"[Dry Run] Would execute: {full_command}")
            # print(f"[Dry Run] With Env Vars: INSTANTLY_API_KEY={client.get('instantly_api_key', 'N/A')}")
        else:
            # Logging Isolation
            log_dir = f"logs/{client_id}"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "latest_run.log")
            
            print(f"   ↳ Logging to: {log_file}")
            
            with open(log_file, "w") as f:
                # We need to construct the environment for the subprocess explicitly
                # run_command helper doesn't support custom env easily without modification.
                # Let's use subprocess directly here for better control and logging redirection.
                
                try:
                    process = subprocess.Popen(
                        full_command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT, # Merge stderr into stdout
                        text=True,
                        env=env_vars
                    )
                    
                    # Stream both to file and console (optional, maybe just file to keep console clean?)
                    # Let's write to file primarily.
                    for line in process.stdout:
                        f.write(line)
                        # Optional: Print a dot or small progress to main console?
                        # print(".", end="", flush=True) 
                    
                    process.wait()
                    
                    if process.returncode != 0:
                        print(f"❌ Failed processing for client {client_id}. Check logs.")
                    else:
                        print(f"✅ Finished processing for client {client_id}")
                except Exception as e:
                    f.write(f"\nCRITICAL ORCHESTRATOR ERROR: {e}\n")
                    print(f"❌ Exception running client {client_id}: {e}")

    print("\n🏁 All clients processed.")

if __name__ == "__main__":
    main()
