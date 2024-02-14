"""Unit tests for the hash register."""

import unittest

from src.hash_register import HashRegister


class HashRegisterTestCase(unittest.TestCase):
    """Unit tests for the hash register class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.register = HashRegister({})

    def test_unchanged_input(self) -> None:
        """Test that an added item is not changed if the input is the same."""
        self.register.set("key", "input", "output")
        self.assertFalse(self.register.is_changed("key", "input"))
        self.assertEqual("output", self.register.get("key"))

    def test_changed_input(self) -> None:
        """Test that an added item is changed if the input is not the same."""
        self.register.set("key", "input", "output")
        self.assertTrue(self.register.is_changed("key", "new input"))

    def test_check_missing(self) -> None:
        """Test that an item that has not been registered is reported as changed."""
        self.assertTrue(self.register.is_changed("key", "input"))
