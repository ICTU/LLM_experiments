import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json

from src.hash_register import HashRegister, load_hashes, save_hashes

class TestHashRegister(unittest.TestCase):

    def setUp(self):
        self.hashes = {
            "file1": ("hash1", "output1"),
            "file2": ("hash2", "output2")
        }
        self.hash_register = HashRegister(self.hashes)

    def test_set_new_key(self):
        self.hash_register.set("file3", "input3", "output3")
        self.assertEqual(self.hash_register.hashes["file3"], ("098f6bcd4621d373cade4e832627b4f6", "output3"))

    def test_set_existing_key(self):
        self.hash_register.set("file1", "new_input", "new_output")
        self.assertEqual(self.hash_register.hashes["file1"], ("0a8e7a1a2d34c7e83c3f4d0e9b8c7d6f", "new_output"))

    def test_get_existing_key(self):
        output = self.hash_register.get("file1")
        self.assertEqual(output, "output1")

    def test_get_nonexistent_key(self):
        with self.assertRaises(KeyError):
            self.hash_register.get("nonexistent_key")

    def test_is_changed_new_key(self):
        self.assertTrue(self.hash_register.is_changed("new_key", "input"))

    def test_is_changed_existing_key_same_input(self):
        self.assertFalse(self.hash_register.is_changed("file1", "output1"))

    def test_is_changed_existing_key_different_input(self):
        self.assertTrue(self.hash_register.is_changed("file1", "new_input"))

    def test_hash_empty_input(self):
        hashed = self.hash_register._hash("")
        self.assertEqual(hashed, "d41d8cd98f00b204e9800998ecf8427e")

    def test_hash_unicode_input(self):
        hashed = self.hash_register._hash("テスト")
        self.assertEqual(hashed, "1fd4bc11f8649d8a1a3a3d5a3a5c5e5f")

class TestLoadSaveHashes(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"file1": ["hash1", "output1"]}))
    def test_load_hashes_file_exists(self, mock_file):
        hash_register = load_hashes(Path("test.json"))
        self.assertEqual(hash_register.hashes, {"file1": ("hash1", "output1")})

    @patch("builtins.open", new_callable=mock_open)
    def test_load_hashes_file_not_exists(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        hash_register = load_hashes(Path("nonexistent.json"))
        self.assertEqual(hash_register.hashes, {})

    @patch("builtins.open", new_callable=mock_open)
    def test_save_hashes(self, mock_file):
        hashes = {"file1": ("hash1", "output1")}
        hash_register = HashRegister(hashes)
        save_hashes(Path("test.json"), hash_register)
        mock_file.assert_called_once_with(Path("test.json"), "w")
        mock_file().write.assert_called_once_with(json.dumps(hashes))

if __name__ == '__main__':
    unittest.main()

# This test suite covers the following scenarios for the HashRegister class:

# 1. Setting a new key-value pair
# 2. Updating an existing key with new input and output
# 3. Getting the output for an existing key
# 4. Handling a nonexistent key when using get()
# 5. Checking if a new key has changed
# 6. Checking if an existing key has changed with the same input
# 7. Checking if an existing key has changed with different input
# 8. Hashing an empty input
# 9. Hashing a Unicode input

# For the load_hashes and save_hashes functions:

# 1. Loading hashes from an existing file
# 2. Handling the case when the file doesn't exist during loading
# 3. Saving hashes to a file

# The tests use mocking to simulate file I/O operations and to isolate the functionality of the HashRegister class. They cover various scenarios related to setting, getting, and checking for changes in the hash register, as well as handling edge cases like nonexistent keys and empty or Unicode inputs.