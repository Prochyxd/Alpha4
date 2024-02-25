import json
import unittest

class TestLoadConfig(unittest.TestCase):
    """
    Test case for the load_config function.
    """

    def test_load_config(self):
        # Prepare
        expected_data = {"key": "value"}

        # Act
        actual_data = load_config()

        # Assert
        self.assertEqual(actual_data, expected_data)

if __name__ == '__main__':
    unittest.main()