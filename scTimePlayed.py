import os
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Modify this path to point to the directory containing Star Citizen log files.
log_directory = r'C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\logbackups'

def parseTimestamp(timestamp_str):
    timestamp_pattern = r'<(\d{2}:\d{2}:\d{2})>|<(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)>'
    
    # Search for the timestamp in the given string.
    match = re.search(timestamp_pattern, timestamp_str)
    if match:
        # If the timestamp is in ISO format, shorten it to ensure consistent format.
        if match.group(2):
            timestamp_long = match.group(2)
            timestamp_short = timestamp_long[11:19] # Extract only the hour, minute, and second.
            return timestamp_short
        else:
            # If it's in short format, return it as is.
            return match.group(1)
    else:
        return None

def calculateTimeDifference(start_time, end_time):
    # Convert times to datetime objects for manipulation.
    start_datetime = datetime.strptime(start_time, '%H:%M:%S') if start_time else None
    end_datetime = datetime.strptime(end_time, '%H:%M:%S') if end_time else None
    
    if start_datetime is None or end_datetime is None:
        return None
    
    # Consider day change if end time is smaller than start time (assuming each session doesn't span multiple days).
    if start_datetime > end_datetime:
        end_datetime += timedelta(days=1)
    
    # Calculate session duration.
    time_difference = end_datetime - start_datetime
    return time_difference

def readLogFile(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
    
    # Find start and end timestamps of the session.
    start_time = None
    end_time = None
    for line in lines:
        timestamp = parseTimestamp(line)
        if timestamp:
            if start_time is None:
                start_time = timestamp
            end_time = timestamp
    
    # Calculate time difference between start and end time.
    if start_time and end_time:
        time_difference = calculateTimeDifference(start_time, end_time)
        return time_difference
    else:
        return None

def main():
    total_playtime = 0
    playtimes = []
    dates = []
    
    for filename in os.listdir(log_directory):
        if filename.endswith('.log'):
            file_path = os.path.join(log_directory, filename)
            playtime = readLogFile(file_path)
            if playtime:
                total_playtime += playtime.total_seconds()
                playtimes.append(playtime.total_seconds() / 3600)  # Convert to hours
                date_str = re.search(r'(\d{2} \w+ \d{2})', filename).group(1)
                date = datetime.strptime(date_str, '%d %b %y').date()
                dates.append(date)
                print(f'Playtime in {filename}: {playtime}.')
    
    # Final result.
    total_playtime_hours = total_playtime // 3600
    total_playtime_minutes = (total_playtime % 3600) // 60
    total_playtime_seconds = total_playtime % 60
    print(f'Total playtime: {int(total_playtime_hours)} hours, {int(total_playtime_minutes)} minutes, {int(total_playtime_seconds)} seconds.')
    
    # Sort dates and corresponding playtimes for plotting.
    sorted_data = sorted(zip(dates, playtimes))
    dates = [x[0] for x in sorted_data]
    playtimes = [x[1] for x in sorted_data]
    
    # Calculate cumulative playtime for plotting.
    cumulative_playtime = [sum(playtimes[:i+1]) for i in range(len(playtimes))]
    
    # Plot final graph.
    fig, ax1 = plt.subplots(figsize=(10, 6))

    colorSession = 'c'
    ax1.set_xlabel('Date.')
    ax1.set_ylabel('Playtime (hours).', color=colorSession)
    ax1.bar(dates, playtimes, label='Playtime per session.', color=colorSession)
    ax1.tick_params(axis='y', labelcolor=colorSession)

    ax2 = ax1.twinx()  
    colorCumulative = 'magenta'
    ax2.plot(dates, cumulative_playtime, label='Cumulative playtime.', linestyle='--', color=colorCumulative)
    ax2.set_ylabel('Cumulative Playtime (hours).', color=colorCumulative)
    ax2.tick_params(axis='y', labelcolor=colorCumulative)

    plt.title('Playtime per session and cumulative playtime.')
    fig.tight_layout()  
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()
