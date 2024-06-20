import anthropic
import os
import sys
from dotenv import load_dotenv
from code_gen.skip_dir import skip_dir, skip_file
from pathlib import Path

load_dotenv()

def unit_test_prompt(codefiles, functionality, unit_test):
    prompt = f"""
Your task is to generate unit tests for a codebase in order to ensure the correctness and robustness of a specific functionality. 

You will receive the content of the codebase as a dictionary where the keys are the filepaths and the values are the content of the files. Here are the relevant files from the codebase:

<codefiles>
{codefiles}
</codefiles>

The specific functionality you should focus on when writing tests is:
{functionality}

Here is the existing unit test code that you should use as a reference and extend upon. This code is written in Python and uses the unittest framework. Your tests should be compatible with this existing codebase and should be written in the same programming language and testing framework.

<unit_test>
{unit_test}
</unit_test>

First, carefully analyze the provided codefiles and identify the key components, functions, and classes that are directly related to implementing the specified functionality. 

Next, come up with a list of potential edge cases, failure scenarios, and unexpected inputs that could occur when using this functionality. Think about how the code should handle these situations.

Then, write a comprehensive set of unit tests in the same programming language as the codebase. These tests should cover the core components you identified, as well as the edge cases and failure scenarios you brainstormed. Make sure your tests are thorough and cover as many potential issues as possible. The goal is to catch any bugs or unintended behavior related to the specified functionality.

Provide ONLY the full code for your generated unit tests. Do not include any other explanations, brainstorming, or text. The code should be directly usable in a script. That means no introductory lines or broad explanations. If you do feel the need to add explanations, place these in comments using a '#' symbol.

Remember, your tests should be focused specifically on {functionality}. Do not worry about testing unrelated parts of the codebase. The key is to write targeted, effective tests that will ensure this key functionality is robust and works as intended, even in unexpected situations.
"""
    return prompt


def call_anthropic_llm(prompt):  
    client = anthropic.Anthropic()
    message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=4000,
    temperature=0,
    system="You are a quality assurance expert that focuses on writing precise unit tests.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]
)
    return message.content[0].text

def generate_unit_test(codefiles, functionality, unit_test):
    """Calls an LLM to generate unit tests for input codefiles focusing on specific functionality"""
    prompt = unit_test_prompt(codefiles, functionality, unit_test)
    return call_anthropic_llm(prompt)


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


def unit_test_for_dir(path:Path, functionality:str, unit_test):
    code_files = get_dir_content(path)
    unit_test = generate_unit_test(codefiles=code_files, functionality=functionality, unit_test=unit_test)
    return unit_test


if __name__ == "__main__":
    unit_test = unit_test_for_dir(
        path="C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/3. Code genAI/metrics/LLM_experiments/1-summarization/src/hash_register.py",
        unit_test="1-summarization/tests/test_hash_register.py",
        functionality=sys.argv[1]
        )
    with open("generated_test_hash_register_extend.py", 'w', encoding='utf-8') as file:
        file.write(unit_test)