import asyncio
import logging
import sys
import platform
import argparse

from bleak import BleakScanner, BleakClient

# Parse command line arguments
parser = argparse.ArgumentParser(description="Bluetooth Heart Rate Monitor")
parser.add_argument("-d", "--device", type=str, help="Target device address")
args = parser.parse_args()

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
            
            # Discover services
            print("\nDiscovering services...")
            services = await self.client.get_services()
            
            print("\n=== Available Services ===")
            for service in services:
                print(f"Service UUID: {service.uuid}")
                print("Characteristics:")
                for char in service.characteristics:
                    print(f"  - {char.uuid}")
            
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
                # Prepare the output string
                output = "\r=== Heart Rate Data Received ===\n"
                
                # Raw data logging
                output += f"Raw Data: {data.hex()}\n"
                
                # Flags interpretation
                flags = data[0]
                output += f"Flags: {bin(flags)}\n"
                
                # Heart rate calculation
                if flags & 0x01:
                    # 16-bit heart rate value
                    heart_rate = int.from_bytes(data[1:3], byteorder='little')
                else:
                    # 8-bit heart rate value
                    heart_rate = data[1]
                
                output += f"💓 Heart Rate: {heart_rate} bpm\n"
                
                # Optional: Additional data interpretation
                if len(data) > 2:
                    output += "Additional Data Present:\n"
                    if flags & 0x02:  # Energy expended present
                        energy = int.from_bytes(data[3:5], byteorder='little')
                        output += f"Energy Expended: {energy} kJ\n"
                    
                    if flags & 0x04:  # RR-Interval present
                        rr_intervals = data[5:]
                        rr_intervals_list = [int.from_bytes(rr_intervals[i:i+2], byteorder='little')/1024 for i in range(0, len(rr_intervals), 2)]
                        output += f"RR Intervals: {rr_intervals_list}\n"
                
                # Print the output, replacing the old output
                sys.stdout.write(output)
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