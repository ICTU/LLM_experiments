# Here is a set of unit tests focused on summarizing code in a directory and handling unexpected data formats:

import unittest
from unittest.mock import patch
from pathlib import Path
import json

from summarize_code import summarize_code, summarize_directory
from src.llm import llm_generate_summary, llm_summarize_summary
from src.skip_dir import skip_dir, skip_file
from src.classes import Summary

class TestSummarizeCode(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        self.test_file = self.test_dir / "test_file.py"
        self.test_file.write_text("def test_func():\n    return 'test'")

    def tearDown(self):
        self.test_file.unlink()
        self.test_dir.rmdir()

    @patch('src.llm.llm_generate_summary')
    def test_summarize_code_valid_file(self, mock_llm_generate_summary):
        mock_llm_generate_summary.return_value = "Test summary"
        summary = summarize_code(self.test_file)
        self.assertEqual(summary.path, str(self.test_file))
        self.assertEqual(summary.summary, "Test summary")

    def test_summarize_code_invalid_file(self):
        invalid_file = self.test_dir / "invalid.txt"
        with self.assertRaises(FileNotFoundError):
            summarize_code(invalid_file)

    def test_summarize_code_empty_file(self):
        empty_file = self.test_dir / "empty.py"
        empty_file.write_text("")
        with self.assertRaises(ValueError):
            summarize_code(empty_file)
        empty_file.unlink()

    def test_summarize_code_binary_file(self):
        binary_file = self.test_dir / "binary.dat"
        binary_file.write_bytes(b"\x00\x01\x02\x03")
        with self.assertRaises(UnicodeDecodeError):
            summarize_code(binary_file)
        binary_file.unlink()

    @patch('src.llm.llm_summarize_summary')
    @patch('src.summarize_code.summarize_code')
    def test_summarize_directory_valid(self, mock_summarize_code, mock_llm_summarize_summary):
        mock_summarize_code.return_value = Summary(path=str(self.test_file), summary="File summary")
        mock_llm_summarize_summary.return_value = "Directory summary"
        
        summary = summarize_directory(self.test_dir)
        self.assertEqual(summary.path, str(self.test_dir))
        self.assertEqual(summary.summary, "Directory summary")
        self.assertEqual(len(summary.summaries), 1)

    def test_summarize_directory_empty(self):
        empty_dir = self.test_dir / "empty_dir"
        empty_dir.mkdir()
        with self.assertRaises(ValueError):
            summarize_directory(empty_dir)
        empty_dir.rmdir()

    def test_summarize_directory_invalid(self):
        invalid_dir = self.test_dir / "invalid_dir"
        with self.assertRaises(FileNotFoundError):
            summarize_directory(invalid_dir)

    def test_summarize_directory_skip_dir(self):
        skip_dir_name = self.test_dir / "skip_dir"
        skip_dir_name.mkdir()
        summary = summarize_directory(self.test_dir)
        self.assertEqual(len(summary.summaries), 1)  # Only test_file, skip_dir is skipped
        skip_dir_name.rmdir()

    def test_summarize_directory_skip_file(self):
        skip_file_name = self.test_dir / "skip.txt"
        skip_file_name.write_text("This file should be skipped")
        summary = summarize_directory(self.test_dir)
        self.assertEqual(len(summary.summaries), 1)  # Only test_file, skip.txt is skipped  
        skip_file_name.unlink()

    @patch('src.llm.llm_generate_summary')
    def test_summarize_code_unexpected_json(self, mock_llm_generate_summary):
        mock_llm_generate_summary.return_value = "Invalid JSON summary"
        json_file = self.test_dir / "data.json"
        json_file.write_text('{"key": "value"')  # Malformed JSON
        
        with self.assertRaises(json.JSONDecodeError):
            summarize_code(json_file)
        
        json_file.unlink()

    @patch('src.llm.llm_generate_summary')
    def test_summarize_code_large_file(self, mock_llm_generate_summary):
        mock_llm_generate_summary.return_value = "Large file summary"
        large_file = self.test_dir / "large_file.py"
        large_file.write_text("a" * 1000000)  # 1MB file
        summary = summarize_code(large_file)
        self.assertEqual(summary.summary, "Large file summary")
        large_file.unlink()

if __name__ == '__main__':
    unittest.main()

# This test suite covers the following scenarios:

# 1. Summarizing a valid code file
# 2. Handling an invalid file path
# 3. Handling an empty code file
# 4. Handling a binary file
# 5. Summarizing a valid directory
# 6. Handling an empty directory
# 7. Handling an invalid directory path  
# 8. Skipping directories based on skip_dir rules
# 9. Skipping files based on skip_file rules
# 10. Handling malformed JSON files
# 11. Summarizing a large code file

# The tests use mocking to isolate the functionality of summarize_code and summarize_directory from the actual LLM calls. They create temporary test files and directories to avoid modifying the actual codebase.