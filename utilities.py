from datetime import datetime
import json 
import os

def current_summary (start_time, y, name, age, weight, sex):
    # Get current time 
    now = datetime.now()

    # Calculate the time difference in HH:MM:SS
    time_diff = now - start_time
    time_diff_str = str(time_diff).split(".")[0]

    # Calculate the maximum and average heart rate and round to 1 decimal
    max_hr = max(y)
    avg_hr = round(sum(y) / len(y), 1)

    # Check if calories burned can be calculated
    if name != "default": 
        # Calculate the time difference in minutes
        duration = (datetime.now() - start_time).total_seconds() / 60

        # calculate_calories_burned(age, weight, heart_rate, duration, sex)
        cb = calculate_calories_burned(age, weight, avg_hr, duration, sex)

        # Create one string with all the information
        summary = f"Time Elapsed: {time_diff_str}, Max HR: {max_hr}, Avg HR: {avg_hr}, kcal: {cb}"
    else:
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

def load_profile(path2profile):
    # Check if the profile exists
    if not os.path.exists(f"{path2profile}"):
        print(f"Error: Profile '{path2profile}' does not exist.")
        exit()

    # Load the profile
    with open(f"{path2profile}", "r") as f:
        profile = json.load(f)

    return profile

def calculate_age(dob):
    # Calculate exact age based on the DOB
    dob = datetime.strptime(dob, "%Y-%m-%d")
    age = round((datetime.now() - dob).days / 365, 2)

    return age

def calculate_calories_burned(age, weight, heart_rate, duration, sex):
    """
    Calculate the number of calories burned
    """
    # Formula to calculate the number of calories burned:
    # Soruce: https://www.omnicalculator.com/sports/calories-burned-by-heart-rate
    # Women:
    # CB = T × (0.4472×H - 0.1263×W + 0.074×A - 20.4022) / 4.184
    # Men:
    # CB = T × (0.6309×H + 0.1988×W + 0.2017×A - 55.0969) / 4.184
    # where:
    #     CB – Number of calories burned;
    #     T – Duration of exercise in minutes;
    #     H – Your average heart rate in beats per minute;
    #     W – Your weight in kilograms; and
    #     A – Your age in years.
    if sex == "female":
        calories_burned = duration * (0.4472 * heart_rate - 0.1263 * weight + 0.074 * age - 20.4022) / 4.184
    elif sex == "male":
        calories_burned = duration * (0.6309 * heart_rate + 0.1988 * weight + 0.2017 * age - 55.0969) / 4.184
    else:
        print("Error: cannot calculate calories burned without correct sex. It needs to be 'male' or 'female'.")
        calories_burned = 0
   
    return round(calories_burned, 1) 