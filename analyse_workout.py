import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Parse command line arguments
parser = argparse.ArgumentParser(description="Profile Manager")
parser.add_argument("-p", "--path", type=str, help="Path to the data to analyse")
args = parser.parse_args()


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

# Remove ".csv" from the path
json_path = csv_path.replace(".csv", "_meta.json")

# Check if the JSON file exists
if os.path.exists(json_path):
    print(f"Metadata file '{json_path}' exists.")
    use_meta = True
else:
    print(f"Metadata file '{json_path}' does not exist.")
    use_meta = False

# Re-create main plot
fig, ax = plt.subplots()
ax.plot(np.arange(1, df.shape[0] + 1), df["Heart Rate"])
ax.set_xlabel('Sample')
ax.set_ylabel('Heart Rate (bpm)')
ax.relim()
ax.autoscale_view()  # Autoscale the view
plt.draw()
plt.show(block=True)

# Save the plot
plt.savefig("workout_plots/heart_rate_plot.png")