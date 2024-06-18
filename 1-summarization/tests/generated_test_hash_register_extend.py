import unittest
from src.hash_register import HashRegister

class TestHashRegister(unittest.TestCase):

    def test_empty_string(self):
        hr = HashRegister()
        result = hr.hash("")
        self.assertEqual(result, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    def test_long_string(self):
        hr = HashRegister()
        long_string = "a" * 1000000  # 1 million character string
        result = hr.hash(long_string)
        self.assertEqual(len(result), 64)  # SHA-256 always returns 64 character hash

    def test_unicode_characters(self):
        hr = HashRegister()
        unicode_string = "Hello, 世界 🌍"
        result = hr.hash(unicode_string)
        self.assertEqual(result, "c52d7d8a9af7f0f121d1a655b8cf341b89ee6e7b7d7eba9eca45d8b081127b50")

    def test_newline_characters(self):
        hr = HashRegister()
        newline_string = "Line1\nLine2\r\nLine3"
        result = hr.hash(newline_string)
        self.assertEqual(result, "4b1f166e9406651d46f5caa40cc01f49e9e2e8e2204c8a54d6c9b6d80c09bbe1")

    def test_leading_trailing_whitespace(self):
        hr = HashRegister()
        whitespace_string = "  hello world  \t"
        result = hr.hash(whitespace_string)
        self.assertEqual(result, "141abc6c5c0c5aa3c1e12b49cd1738e0af7e6ca1d9d139b1a1b5e5fbc5d4c20e")

    def test_hash_already_exists(self):
        hr = HashRegister()
        hr.hash("duplicate")
        with self.assertRaises(ValueError):
            hr.hash("duplicate")

    def test_hash_limit_exceeded(self):
        hr = HashRegister(max_size=2)
        hr.hash("one")
        hr.hash("two") 
        with self.assertRaises(ValueError):
            hr.hash("three")

    def test_hash_eviction(self):
        hr = HashRegister(max_size=2)
        first = hr.hash("first")
        second = hr.hash("second")
        third = hr.hash("third")
        self.assertNotIn(first, hr.hashes)
        self.assertIn(second, hr.hashes)
        self.assertIn(third, hr.hashes)

if __name__ == '__main__':
    unittest.main()