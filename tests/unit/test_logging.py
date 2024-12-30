import unittest
from unittest.mock import patch
import logging
from pyavrio.logging import get_logger, LEVEL

class MockLogger(logging.Logger):
    def __init__(self, name, level):
        super().__init__(name, level)
        self.setLevel(level)

class TestGetLogger(unittest.TestCase):
    @patch('logging.getLogger')
    def test_get_logger_default_level(self, mock_getLogger):
        # Configure mock getLogger to return an instance of MockLogger
        mock_logger = MockLogger('test_logger', LEVEL)
        mock_getLogger.return_value = mock_logger

        # Call the function with default log_level=None
        logger = get_logger('test_logger')

        # Check if getLogger was called with the correct arguments
        mock_getLogger.assert_called_once_with('test_logger')

        # Check if logger.level is set to the default LEVEL
        self.assertEqual(logger.level, LEVEL)

    @patch('logging.getLogger')
    def test_get_logger_custom_level(self, mock_getLogger):
        # Configure mock getLogger to return an instance of MockLogger
        custom_level = logging.DEBUG
        mock_logger = MockLogger('test_logger', custom_level)
        mock_getLogger.return_value = mock_logger

        # Call the function with a custom log_level
        logger = get_logger('test_logger', log_level=custom_level)

        # Check if getLogger was called with the correct arguments
        mock_getLogger.assert_called_once_with('test_logger')

        # Check if logger.level is set to the custom_level
        self.assertEqual(logger.level, custom_level)

if __name__ == '__main__':
    unittest.main()
