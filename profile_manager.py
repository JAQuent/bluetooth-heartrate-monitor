import argparse
from utilities import profile_set_up, load_profile
from datetime import datetime

# Parse command line arguments
parser = argparse.ArgumentParser(description="Profile Manager")
parser.add_argument("-a", "--add", action="store_true", help="Create a new profile")
parser.add_argument("-s", "--show", action="store_true", help="Show a  profile")
parser.add_argument("-n", "--name", type=str, help="Target device address")
args = parser.parse_args()

# Check if the arguments are compatible
if args.add and args.show:
    print("Error: You cannot use --add and --show at the same time.")
    exit()

# Create a new profile
if args.add:
    profile_set_up(args.name)

# Show a profile
if args.show:
    print("Showing requested profile...\n")
    profile = load_profile(args.name)

    # Calculate exact age based on the DOB
    dob = datetime.strptime(profile["dob"], "%Y-%m-%d")
    age = round((datetime.now() - dob).days / 365, 2)

    # Print the profile
    print(profile)
    print("\nCalculating age...")
    print(f"Age: {age} years")
