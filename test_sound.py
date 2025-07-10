#!/usr/bin/env python3
"""
Test script for the warning sound functionality
"""

import time
from utilities import play_warning_sound

def test_sound():
    print("Testing warning sound functionality...")
    print("You should hear a sound in 2 seconds...")
    time.sleep(2)
    
    print("Playing sound now...")
    play_warning_sound()
    
    print("Sound test completed!")
    print("\nIf you didn't hear anything, try:")
    print("1. Check your system volume")
    print("2. Install required audio packages: sudo apt install pulseaudio-utils alsa-utils")
    print("3. Test system bell: echo -e '\\a'")

if __name__ == "__main__":
    test_sound()
