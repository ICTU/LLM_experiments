import os
import box
import yaml
import math
from pathlib import Path
from summarize_code import skip_dir, skip_file

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))



def number_of_files(dir_path):
    """Count number of files in a directory"""
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file() and not skip_file(Path(path)):
            print(path)
            count += 1
        if path.is_dir() and not skip_dir(Path(path)):
            count += number_of_files(path)
        else: continue
    return count

# def number_of_directories(dir_path):
#     """Count number of directories in directory"""
#     count = 0
#     for dir in os.scandir(dir_path):
#         if dir.is_dir() and not skip_dir(Path(dir)):
#             count += 1
#         else: continue
#     return count

def max_num_tokens(path):
    """Calculate the max numer of tokens usable in the output, takes base tokens en number of files as int input"""
    #if no files in dir..
    number_of_files_in_dir = number_of_files(path)
    max_num_tokens = math.ceil(cfg.BASE_MAX_TOKENS_SUM + math.sqrt(number_of_files_in_dir * 25))
    return max_num_tokens

#testing
#print(number_of_files(os.path.dirname(os.path.realpath(__file__))))
#print(number_of_directories(os.path.dirname(os.path.realpath(__file__))))
#print(max_num_tokens(os.path.dirname(os.path.realpath(__file__))))
