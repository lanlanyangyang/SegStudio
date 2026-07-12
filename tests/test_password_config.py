import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from config import settings


class PasswordConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        settings.PASSWORD_FILE = os.path.join(self.temp_dir.name, "password.json")
        settings.DEFAULT_ADMIN_PASSWORD = "123456"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_password_round_trip(self):
        self.assertEqual(settings.get_admin_password(), "123456")
        settings.set_admin_password("654321")
        self.assertEqual(settings.get_admin_password(), "654321")

    def test_password_validation(self):
        self.assertTrue(settings.is_admin_password_correct("123456"))
        self.assertFalse(settings.is_admin_password_correct("wrong"))


if __name__ == "__main__":
    unittest.main()
