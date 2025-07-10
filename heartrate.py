import asyncio
import logging
import sys
import platform
import argparse
import csv
import os
import time
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from utilities import current_summary, load_profile, calculate_age, play_warning_sound
import json 

from bleak import BleakScanner, BleakClient

# Parse command line arguments
parser = argparse.ArgumentParser(description="Bluetooth Heart Rate Monitor")
parser.add_argument("-d", "--device", type=str, help="Target device address")
parser.add_argument("-g", "--graph", action="store_true", help="Display live heart rate graph")
parser.add_argument("-n", "--name", type=str, help="Target device address")
parser.add_argument("-t", "--target", type=int, help="Target heart rate (bpm)")
args = parser.parse_args()

# If there is not data folder, create it
try:
    os.mkdir("data")
except FileExistsError:
    pass

# Load the profile
if args.name:
    print("=== Loading profile ===")
    name = args.name
    path2profile = f"configs/{name}.json"
    profile = load_profile(path2profile)

    # Calculate exact age based on the DOB
    age = calculate_age(profile["dob"])
    weight = float(profile["weight"])
    sex = profile["sex"]

    # Print the profile
    print(profile)
    print("\nCalculating age...\n")
    print(f"Age: {age} years")
else:
    name = "default"
    age = 0
    weight = 0
    sex = "unknown"
    print("No profile selected...")

# Set target heart rate
target_hr = args.target if args.target else None
if target_hr:
    print(f"Target heart rate set to: {target_hr} bpm")

# Create a CSV file to store the data with the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"data/heartrate_data_{name}_{timestamp}.csv"

# Print the header
print("\n=== Starting heart rate monitor ===")

# Print the CSV filename
print(f"The data will be written to: {csv_filename}")

# Open the CSV file and write the header
with open(csv_filename, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Timestamp", "Heart Rate"])

if name != "default":
    # Strip .csv from the filename
    meta_data_filename = csv_filename.replace(".csv", "_meta.json")

    # Copy profile to the data folder and add target_hr if specified
    workout_metadata = profile.copy()  # Copy the profile data
    if target_hr:
        workout_metadata["target_hr"] = target_hr  # Add target HR to workout metadata
    
    with open(meta_data_filename, "w") as file:
        json.dump(workout_metadata, file)
    print(f"Profile saved to {meta_data_filename}")
    if target_hr:
        print(f"Target HR {target_hr} bpm saved to workout metadata")

# Set the target device address if provided
if args.device:
    TARGET_DEVICE_ADDRESS = args.device
    # Print the target device address
    print(f"Target Device Address: {TARGET_DEVICE_ADDRESS}")

# Heart Rate Service and Characteristic UUIDs
HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Global flag for graceful shutdown
shutdown_flag = False

def monitor_input():
    """Monitor for user input to gracefully shutdown"""
    global shutdown_flag
    try:
        input("Press Enter to stop monitoring and save data...\n")
        shutdown_flag = True
    except EOFError:
        # Handle case where input is not available (like in some environments)
        pass

class DetailedHeartRateMonitor:
    def __init__(self, target_address=TARGET_DEVICE_ADDRESS):
        self.target_address = target_address
        self.client = None
        self.is_connected = False
        self.last_warning_time = 0  # Track last warning sound time

    async def scan_and_connect(self):
        """
        Comprehensive scanning and connection process with detailed logging.
        """
        print("Starting comprehensive Bluetooth device scanning...")
        
        try:
            # Detailed device scanning
            print("Scanning for Bluetooth LE devices...")
            devices = await BleakScanner.discover()
            
            print("\n=== Discovered Devices ===")
            for device in devices:
                print(f"Device Name: {device.name}")
                print(f"Device Address: {device.address}")
                print("---")
            
            # Find target device
            target_device = next(
                (device for device in devices if device.address == self.target_address), 
                None
            )
            
            if not target_device:
                print(f"\n❌ Target device {self.target_address} not found.")
                return False
            
            print(f"\n✅ Target device found: {target_device.name}")
            
            # Attempt connection
            print("\nAttempting to connect...")
            self.client = BleakClient(self.target_address)
            await self.client.connect(timeout=30.0)  # Time out after 30 seconds
            
            self.is_connected = True
            print("✅ Successfully connected to the heart rate monitor!")
            
            return True
        
        except Exception as e:
            print(f"\n❌ Connection Error: {e}")
            return False

    async def monitor_heart_rate(self):
        """
        Monitor heart rate with detailed error handling and logging.
        """
        if not self.is_connected:
            print("Not connected to the device.")
            return
        
        def heart_rate_handler(sender, data):
            """
            Process and log heart rate data with detailed breakdown.
            """
            try:
                # Flags interpretation
                flags = data[0]
                
                # Heart rate calculation
                if flags & 0x01:
                    # 16-bit heart rate value
                    heart_rate = int.from_bytes(data[1:3], byteorder='little')
                else:
                    # 8-bit heart rate value
                    heart_rate = data[1]
                
                # Write the data to the CSV file
                with open(csv_filename, mode='a', newline='') as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), heart_rate])

                # Print the heart rate, replacing the old output
                sys.stdout.write(f"\r💓 Heart Rate: {heart_rate} bpm")
                if target_hr:
                    sys.stdout.write(f" (Target: {target_hr} bpm)")
                sys.stdout.flush()

                # Check if we need to play warning sound (if below target)
                if target_hr and heart_rate < target_hr:
                    current_time = time.time()
                    if current_time - self.last_warning_time >= 5:  # 5 seconds interval
                        play_warning_sound()
                        self.last_warning_time = current_time

                # If --graph is provided, update the plot
                if args.graph:
                    # Update the data
                    x.append(len(x))
                    y.append(heart_rate)

                    # Calculate the summary
                    summary = current_summary(start_time, y, name, age, weight, sex)

                    # Add title to the plot
                    ax.set_title(summary)
                    
                    # Update background color based on target HR
                    if target_hr:
                        if heart_rate < target_hr:
                            ax.set_facecolor('#ffcccc')  # Pastel red
                        else:
                            ax.set_facecolor('#ccffcc')  # Pastel green
                    
                    # Update the plot
                    line.set_xdata(x)
                    line.set_ydata(y)
                    ax.relim()
                    ax.autoscale_view()  # Autoscale the view
                    plt.draw()
                    plt.pause(0.01)  # Pause to allow the plot to update
                
            
            except Exception as e:
                print(f"Error processing heart rate data: {e}")
        
        try:
            print("\nStarting Heart Rate Monitoring...")
            # Start monitoring heart rate time stamp
            start_time = datetime.now()

            # If --graph is provided, display the live heart rate graph
            if args.graph:
                # Print using graph
                print("Initializing live heart rate graph...")

                # Initialize the plot
                plt.ion()  # Turn on interactive mode
                fig, ax = plt.subplots()
                x, y = [], []
                line, = ax.plot(x, y, color='black')  # Changed to black for better visibility
                ax.set_xlabel('Sample')
                ax.set_ylabel('Heart Rate (bpm)')
                
                # Add target HR line if specified
                if target_hr:
                    ax.axhline(y=target_hr, color='red', linestyle='--', alpha=0.7)

            await self.client.start_notify(
                HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID, 
                heart_rate_handler
            )
            
            # Start input monitoring thread
            input_thread = threading.Thread(target=monitor_input, daemon=True)
            input_thread.start()
            
            # Keep monitoring until user stops or shutdown flag is set
            while not shutdown_flag:
                await asyncio.sleep(0.1)  # Reduced sleep time for more responsive shutdown
                
            print("\n✅ Stopping monitoring gracefully...")
        
        except Exception as e:
            print(f"Monitoring Error: {e}")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """
        Stop heart rate monitoring and disconnect gracefully.
        """
        if self.client and self.is_connected:
            try:
                await self.client.stop_notify(HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID)
                await self.client.disconnect()
                self.is_connected = False
                print("✅ Disconnected from heart rate monitor")
            except Exception as e:
                print(f"⚠️  Disconnection warning: {e}")
        else:
            print("✅ No active connection to disconnect")

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Heart Rate Monitor
    hrm = DetailedHeartRateMonitor()
    
    try:
        # Connect to device
        connection_success = await hrm.scan_and_connect()
        
        if connection_success:
            # Start monitoring
            await hrm.monitor_heart_rate()
    
    except KeyboardInterrupt:
        print("\n⚠️  Keyboard interrupt received, stopping gracefully...")
        global shutdown_flag
        shutdown_flag = True
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        await hrm.stop_monitoring()
        print("💾 Data saved successfully. Program terminated.")

if __name__ == "__main__":
    if platform.system() == "Linux" and sys.platform != "darwin":
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    asyncio.run(main())