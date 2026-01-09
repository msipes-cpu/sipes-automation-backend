import os
import sys
try:
    from execution.clickup_manager import get_teams, get_spaces
except ImportError:
    sys.path.append(os.getcwd())
    from execution.clickup_manager import get_teams, get_spaces

try:
    team = get_teams()
    print(f"Team: {team['name']} (ID: {team['id']})")
    
    spaces = get_spaces(team['id'])
    print("\nAvailable Spaces:")
    for s in spaces:
        print(f"- {s['name']} (ID: {s['id']})")
        
except Exception as e:
    print(f"Error: {e}")
