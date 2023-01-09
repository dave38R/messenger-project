'''
this script has the purpose of translating all the ascii letters into latin-1 which understands accents like é, è, à, ^ and all others. 
It avoids having json files with weird caracters like /u12aar456/ instead of a simple é. 
This should be run once on newly acquired json files.
'''

import json 
import os
import datetime
import pytz
from tqdm import tqdm

# A function that returns all the json files in a given directory
def get_json_files(dir):
    json_files = []
    for file in os.listdir(dir):
        if file.endswith(".json"):
            json_files.append(file)
    return json_files

# A program that, upon seeing the string 'ptp_original' will return the string 'ptp'
def get_root_name(dir):
    return dir.split('_')[-2]

# A function that takes in a path and returns the last folder name
def get_last_folder_name(dir):
    return dir.split('\\')[-1]

# A function that takes in a json message and converts the timestamp_ms value to a datetime object
def convert_timestamp_to_datetime(messages):
    for message in messages:
        # Convert the timestamp_ms value to a datetime object
        timestamp = message['timestamp_ms']
        date_time = datetime.datetime.fromtimestamp(timestamp / 1000)
        # Specify the timezone you want to use
        timezone = pytz.timezone('Europe/Paris')
        # Convert the datetime object to a timezone-aware datetime object
        date_time_tz = timezone.localize(date_time)
        # Convert the timezone-aware datetime object to a string in the desired format
        date_time_str = date_time_tz.strftime('%d %B, %Y - %H:%M:%S')
        # Delete the timestamp_ms key and add the new datetime key
        del message['timestamp_ms']
        message['datetime'] = date_time_str
    return messages

# A function that looks at the folder input, looks at all the json files and saves the participants in a new json file called 'participants.json' and save the messages in a new json file called 'ptp_messages.json'
def save_participants_and_messages(dir):
    # We define the new directory name
    new_dir = get_root_name(get_last_folder_name(dir))
    # Get all the json files in the folder
    json_files = get_json_files(dir)
    pbar = tqdm(total=len(json_files))
    # Loop through each JSON file
    for i, json_file in enumerate(json_files):
        # Create a list to store the participants from all the files
        participants = []
        # Create a list to store the messages from all the files
        messages = []

        # Load the JSON data from the input file
        with open(dir + '\\' + json_file, "r", encoding='utf-8') as f:
            data = json.load(f)
            # Get the "participants" key from the data
            participants += data["participants"]
            # Get the "messages" key from the data
            messages += data["messages"]

        # Save the "participants" data to a new JSON file
        with open(new_dir + '\\' + "participants.json", "w", encoding='utf-8') as f:
            json.dump(participants, f, ensure_ascii=False, indent=4)

        # Save the "messages" data to a new JSON file
        messages = convert_timestamp_to_datetime(messages)
        with open(new_dir + '\\' + new_dir + "_messages" + str(i) + ".json", "w", encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        pbar.update(1)
        



if __name__ == "__main__":
    save_participants_and_messages('.\original_data\ptp_original')
    save_participants_and_messages('.\original_data\zoo_original')
    # Save for testing purposes
    # print(get_root_name(get_last_folder_name('.\ptp_original')))
    # print(get_root_name(get_last_folder_name('.\zoo_original')))



