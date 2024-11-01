import asyncio
import logging
import sys
import platform
import argparse
import csv
import os
from datetime import datetime

from bleak import BleakScanner, BleakClient

# Parse command line arguments
parser = argparse.ArgumentParser(description="Bluetooth Heart Rate Monitor")
parser.add_argument("-d", "--device", type=str, help="Target device address")
args = parser.parse_args()

# If there is not data folder, create it
try:
    os.mkdir("data")
except FileExistsError:
    pass

# Create a CSV file to store the data with the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"data/heartrate_data_{timestamp}.csv"

# Print the header
print("\n=== Starting heart rate monitor ===")

# Print the CSV filename
print(f"The data will be written to: {csv_filename}")

# Open the CSV file and write the header
with open(csv_filename, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Timestamp", "Heart Rate"])

# Set the target device address if provided
if args.device:
    TARGET_DEVICE_ADDRESS = args.device
    # Print the target device address
    print(f"Target Device Address: {TARGET_DEVICE_ADDRESS}")

# Heart Rate Service and Characteristic UUIDs
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

class DetailedHeartRateMonitor:
    def __init__(self, target_address=TARGET_DEVICE_ADDRESS):
        self.target_address = target_address
        self.client = None
        self.is_connected = False

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
                sys.stdout.flush()
                
            
            except Exception as e:
                print(f"Error processing heart rate data: {e}")
        
        try:
            print("\nStarting Heart Rate Monitoring...")
            await self.client.start_notify(
                HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID, 
                heart_rate_handler
            )
            
            # Keep monitoring until user stops
            while True:
                await asyncio.sleep(1)
        
        except Exception as e:
            print(f"Monitoring Error: {e}")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """
        Stop heart rate monitoring and disconnect.
        """
        if self.client and self.is_connected:
            try:
                await self.client.stop_notify(HEART_RATE_MEASUREMENT_CHARACTERISTIC_UUID)
                await self.client.disconnect()
                print("\n✅ Disconnected from heart rate monitor")
            except Exception as e:
                print(f"Disconnection Error: {e}")

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
        print("\nMonitoring stopped by user.")
    
    finally:
        await hrm.stop_monitoring()

if __name__ == "__main__":
    if platform.system() == "Linux" and sys.platform != "darwin":
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    asyncio.run(main())