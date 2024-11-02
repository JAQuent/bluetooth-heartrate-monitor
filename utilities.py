from datetime import datetime
import json 
import os

def current_summary (start_time, y):
    # Get current time 
    now = datetime.now()

    # Calculate the time difference in HH:MM:SS
    time_diff = now - start_time
    time_diff_str = str(time_diff).split(".")[0]

    # Calculate the maximum and average heart rate and round to 1 decimal
    max_hr = max(y)
    avg_hr = round(sum(y) / len(y), 1)
    
    # Create one string with all the information
    summary = f"Time Elapsed: {time_diff_str}, Max HR: {max_hr}, Avg HR: {avg_hr}"

    # Return the summary
    return summary

def ask_for_profile_input():
    # Ask for the user's DOB, weight and sex
    dob = input("Enter your date of birth (YYYY-MM-DD): ")
    weight = input("Enter your weight (kg): ")
    sex = input("Type 'male' or 'female': ")

    # Validate the input
    ## Check if DOB is in the correct format
    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        print("Error: DOB should be in the format YYYY-MM-DD")
        exit()

    ## Check if weight is a number
    try:
        float(weight)
    except ValueError:
        print("Error: Weight should be a number")
        exit()

    ## Check if sex if either male or female
    if sex != "male" and sex != "female":
        print("Please use either 'male' or 'female'")
        exit()

    return dob, weight, sex

def profile_set_up(name):
    # Print the profile manager
    print("\n")
    print("Creating a new profile...\n")
    print(f"Profile name: {name}")

    # Get profile input
    dob, weight, sex = ask_for_profile_input()

    # Create a Python object (dict):
    new_profile = {
        "name": name,
        "dob": dob,
        "weight": weight,
        "sex": sex
        }

    # Print
    print(new_profile)

    # Ask for confirmation
    confirm = input("Is the information correct (y/n): ")
    while confirm != "y":
        print("Please re-enter the information:\n\n")
        dob, weight, sex = ask_for_profile_input()
        x = {
            "name": name,
            "dob": dob,
            "weight": weight,
            "sex": sex
        }
        print(new_profile)
        confirm = input("Is the information correct (y/n): ")

    # Convert into JSON:
    new_profile_json = json.dumps(new_profile)

    # Create configs folder if it doesn't exist
    if not os.path.exists("configs"):
        os.makedirs("configs")
    
    # Save the profile to a file
    with open(f"configs/{name}.json", "w") as f:
        f.write(new_profile_json)

def load_profile(name):
    # Check if the profile exists
    if not os.path.exists(f"configs/{name}.json"):
        print(f"Error: Profile '{name}' does not exist.")
        exit()

    # Load the profile
    with open(f"configs/{name}.json", "r") as f:
        profile = json.load(f)

    return profile