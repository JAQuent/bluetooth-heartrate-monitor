from datetime import datetime

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