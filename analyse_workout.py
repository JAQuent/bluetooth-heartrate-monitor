import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utilities import calculate_calories_burned, get_heart_rate_zones, calculate_age
import json

####################################################################
# Parse command line arguments
parser = argparse.ArgumentParser(description="Profile Manager")
parser.add_argument("-p", "--path", type=str, help="Path to the data to analyse")
args = parser.parse_args()

####################################################################
# Check if provided path exists
if not os.path.exists(args.path):
    print(f"Error: Path '{args.path}' does not exist.")
    exit()
else:
    print(f"Data in '{args.path}' exists.")
    csv_path = args.path

# Load .csv as a pandas DataFrame
print(f"Loading data from '{csv_path}'...")
df = pd.read_csv(csv_path)

# Remove ".csv" from the path and add "_meta.json"
workout_name = csv_path.replace(".csv", "").split("/")[-1]
json_path = 'data/' + workout_name + "_meta.json"

# Check if the JSON file exists
if os.path.exists(json_path):
    print(f"Metadata file '{json_path}' exists.")
    use_meta = True
else:
    print(f"Metadata file '{json_path}' does not exist.")
    use_meta = False

####################################################################
# Caclulate the duration of the workout in HH:MM:SS
## Convert first column to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
## Calculate the time difference between beginning and end
duration = df["Timestamp"].iloc[-1] - df["Timestamp"].iloc[0]
## Convert the time difference to HH:MM:SS and remove days
duration_str = str(duration).split(".")[0].split(" ")[-1]
## Calculate the duration in minutes
duration_min = duration.total_seconds() / 60

# Calculate the average heart rate
avg_hr = round(df["Heart Rate"].mean(), 1)
# Calculate the maximum heart rate
max_hr = df["Heart Rate"].max()

# Calculate the calories burned
if use_meta:
    with open(json_path, "r") as file:
        meta_data = json.load(file)
    weight = float(meta_data["weight"])
    sex = meta_data["sex"]
    max_hr_meta = float(meta_data["max_hr"])
    name = meta_data["name"]

    # Calculate exact age based on the DOB
    age = calculate_age(meta_data["dob"])

    # Calculate the calories burned
    cb = calculate_calories_burned(age, weight, avg_hr, duration_min, sex)

    # Calculate heart rate zones
    hr_zones = get_heart_rate_zones(max_hr_meta)

    # Create one string with all the information
    summary = f"Duration: {duration_str}, Max HR: {max_hr}, Avg HR: {avg_hr}, kcal: {cb}"
else:
    # Create one string with all the information
    summary = f"Duration: {duration_str}, Max HR: {max_hr}, Avg HR: {avg_hr}"


####################################################################
# Re-create main plot with 1 x 2 layout
fig, ax = plt.subplots(1,2,figsize=(12,6))
ax[0].plot(np.arange(1, df.shape[0] + 1), df["Heart Rate"])
ax[0].set_xlabel('Sample')
ax[0].set_ylabel('Heart Rate (bpm)')
ax[0].set_title(summary)                   
ax[0].relim()
ax[0].autoscale_view()

####################################################################
# Calculate time spend in each heart rate zone
    # Zone 1	Very light	50–60%
    # Zone 2	Light	    60–70%
    # Zone 3	Moderate    70–80%
    # Zone 4	Hard	    80–90%
    # Zone 5	Maximum	    90–100%
if use_meta:
    # Prepare the heart rate zones
    hr_zones_labels = ["Rest", "Very light", "Light", "Moderate", "Hard", "Maximum"]
    hr_zones_colours = ["#FFFFFF", "#C8C8C8", "#3AD3F4", "#73B42B", "#FFD100", "#E70067"]
    hr_zones_values = []

    # Calculate the time spent in each zone by summing boolean
    hr_zones_values.append(sum(df["Heart Rate"] < hr_zones['zone1'][0]))
    hr_zones_values.append(sum((df["Heart Rate"] >= hr_zones['zone1'][0]) & (df["Heart Rate"] < hr_zones['zone1'][1])))
    hr_zones_values.append(sum((df["Heart Rate"] >= hr_zones['zone2'][0]) & (df["Heart Rate"] < hr_zones['zone2'][1])))
    hr_zones_values.append(sum((df["Heart Rate"] >= hr_zones['zone3'][0]) & (df["Heart Rate"] < hr_zones['zone3'][1])))
    hr_zones_values.append(sum((df["Heart Rate"] >= hr_zones['zone4'][0]) & (df["Heart Rate"] < hr_zones['zone4'][1])))
    hr_zones_values.append(sum(df["Heart Rate"] >= hr_zones['zone5'][0]))

    # Drop zone that is zero
    hr_zones_labels = [label for label, value in zip(hr_zones_labels, hr_zones_values) if value > 0]
    hr_zones_colours = [colour for colour, value in zip(hr_zones_colours, hr_zones_values) if value > 0]
    hr_zones_values = [value for value in hr_zones_values if value > 0]

    # # Create a pie chart using hr_zones_colours
    ax[1].pie(hr_zones_values, labels=hr_zones_labels, autopct='%1.1f%%', colors=hr_zones_colours)
    ax[1].set_title("Heart Rate Zones")

####################################################################
# Add a title to the plot
# Get date from workout_name (e.g. 'heartrate_data_mengya_20241109_184307')
date = workout_name.split("_")[3]
time = workout_name.split("_")[4]
date = date[:4] + "-" + date[4:6] + "-" + date[6:]
time = time[:2] + ":" + time[2:4]

plt.suptitle(f"Workout summary from {date} {time} by {name}",fontsize = 16)

####################################################################
# Save the plot
# Create workout_plots directory 
if not os.path.exists("workout_plots"):
    os.mkdir("workout_plots")

# Save the plot
plt.savefig("workout_plots/" + workout_name + ".png")

# Show
plt.show(block=True)