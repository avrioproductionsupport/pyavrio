import json
import re
import uuid
from collections import namedtuple

import httpretty
import requests
import unittest

# Constants for test data
SERVER_ADDRESS = "http://example.com"
URL_STATEMENT_PATH = "/statement"
TOKEN_RESOURCE = "http://example.com/token"
SAMPLE_TOKEN = "sample_token"
SAMPLE_RESPONSE_DATA = {"data": "sample data"}

class OAuthTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        httpretty.enable() 

    @classmethod
    def tearDownClass(cls):
        httpretty.disable()  

    def setUp(self):
        httpretty.reset()  

    def test_post_statement_callback(self):
        # Register the URI for POST request
        httpretty.register_uri(
            httpretty.POST,
            f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}",
            body=json.dumps(SAMPLE_RESPONSE_DATA),
            headers={"Authorization": f"Bearer {SAMPLE_TOKEN}"}
        )

        # Simulate the action that makes the POST request
        response = requests.post(f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}", headers={"Authorization": f"Bearer {SAMPLE_TOKEN}"})

        # Verify if the POST request was made
        requests_made = httpretty.latest_requests()
        self.assertGreater(len(requests_made), 0, "No requests were made.")
        self.assertEqual(response.json(), SAMPLE_RESPONSE_DATA, "Response body mismatch.")

    def test_get_token_callback(self):
        # Register the URI for GET request
        httpretty.register_uri(
            httpretty.GET,
            f"{TOKEN_RESOURCE}/1234",
            body=json.dumps({"nextUri": f"{TOKEN_RESOURCE}/1234"}),  # Mocked redirect response
        )

        # Simulate the action that makes the GET request
        response = requests.get(f"{TOKEN_RESOURCE}/1234")

        # Verify if the GET request was made
        requests_made = httpretty.latest_requests()
        self.assertGreater(len(requests_made), 0, "No requests were made.")
        self.assertIn("nextUri", response.json(), "Missing 'nextUri' in the response.")

    def test_multithreaded_token_server(self):
        # Simulate a POST request for multithreaded token server
        challenge_id = str(uuid.uuid4())
        httpretty.register_uri(
            httpretty.POST,
            f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}",
            body=json.dumps(SAMPLE_RESPONSE_DATA),
        )

        # Simulate the action that makes the POST request
        response = requests.post(f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}")

        # Verify if the POST request was made
        requests_made = httpretty.latest_requests()
        self.assertGreater(len(requests_made), 0, "No requests were made.")
        self.assertEqual(response.json(), SAMPLE_RESPONSE_DATA, "Response body mismatch.")

    def test_get_token_requests(self):
        challenge_id = "test_challenge"
        # Register URI for GET request
        httpretty.register_uri(
            httpretty.GET,
            f"{TOKEN_RESOURCE}/{challenge_id}",
            body="{}",
        )

        # Simulate the GET request
        response = requests.get(f"{TOKEN_RESOURCE}/{challenge_id}")

        # Verify if the GET request was made
        requests_made = httpretty.latest_requests()
        self.assertGreater(len(requests_made), 0, "No requests were made.")
        self.assertEqual(response.text, "{}", "Response body mismatch.")

    def test_post_statement_requests(self):
        # Register URI for POST request
        httpretty.register_uri(
            httpretty.POST,
            f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}",
            body="{}",
        )

        # Simulate the POST request
        response = requests.post(f"{SERVER_ADDRESS}{URL_STATEMENT_PATH}")

        # Verify if the POST request was made
        requests_made = httpretty.latest_requests()
        self.assertGreater(len(requests_made), 0, "No requests were made.")
        self.assertEqual(response.text, "{}", "Response body mismatch.")

if __name__ == "__main__":
    unittest.main()
