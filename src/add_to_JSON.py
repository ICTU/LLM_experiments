# Python script to update JSON 
import json
import box
import yaml

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))
 
# function to add to JSON
def write_json(new_data, filename=cfg.JSON_FILE_NAME):
    with open(filename,'r+') as file:
        # load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside chosen experiment
        file_data[cfg.JSON_EXPERIMENT_NAME].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
 
