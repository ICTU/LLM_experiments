import os
from skip_dir import skip_dir, skip_file
from pathlib import Path


def get_dir_files(path:Path) -> list[Path]:
    file_paths = []
    for root, dirs, files in os.walk(path):
        # Filter out skipped directories
        dirs[:] = [d for d in dirs if not skip_dir(Path(root) / d)]
        
        for file in files:
            file_path = Path(root) / file
            if not skip_file(file_path):
                    file_paths.append(file_path)
    return file_paths

def get_dir_content(path:Path) -> dict:
    file_content = {}
    for file_path in get_dir_files(path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content[file_path] = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    file_content[file_path] = f.read()
            except UnicodeDecodeError:
                print(f"Skipping file: {file_path} (unsupported encoding)")
    return file_content



#load files
concatenated_content = get_dir_content("C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/3. Code genAI/metrics/LLM_experiments/1-summarization/src/hash_register.py")

functionality = "extending the hash register unit test"

with open("C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/3. Code genAI/metrics/LLM_experiments/1-summarization/tests/test_hash_register.py", 'r', encoding='utf-8') as f:
    unit_test = f.read()