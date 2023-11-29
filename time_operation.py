import time
import pytz
from datetime import datetime

# Set the start time
start_time = time.time()

# Define the duration in seconds (1 hour = 3600 seconds)
duration = 1

# Get the time zone for the Philippines
ph_timezone = pytz.timezone('Asia/Manila')

# Run the loop until the duration is reached
while time.time() - start_time < duration:
    # Get the current time in the Philippines' time zone
    current_time = datetime.now(ph_timezone)

    # Format and print only the date, hours, and minutes
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M")
    print("Current time in the Philippines:", formatted_time)
