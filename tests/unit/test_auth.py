import unittest
from unittest.mock import MagicMock
from pyavrio.auth import AvrioAuthentication, _BearerAuth
from requests import PreparedRequest, Session
from pyavrio.auth import Authentication


class TestAuthentication(unittest.TestCase):
    def test_set_http_session(self):
        class MockAuth(Authentication):
            def set_http_session(self, http_session: Session) -> Session:
                return http_session

        auth = MockAuth()
        http_session = Session()

        result_session = auth.set_http_session(http_session)

        self.assertEqual(result_session, http_session)

    def test_get_exceptions(self):
        class MockAuth(Authentication):
            def set_http_session(self, http_session: Session) -> Session:
                return http_session

        auth = MockAuth()

        exceptions = auth.get_exceptions()

        self.assertEqual(exceptions, ())


class TestAvrioAuthentication(unittest.TestCase):
    def setUp(self):
        self.token = "dummy_token"
        self.auth = AvrioAuthentication(self.token)
        self.http_session = Session()

    def test_set_http_session(self):
        # Test setting the HTTP session
        result_session = self.auth.set_http_session(self.http_session)
        self.assertEqual(result_session.auth.token, self.token)

    def test_get_exceptions(self):
        # Call get_exceptions method and assert the return value
        exceptions = self.auth.get_exceptions()
        self.assertEqual(exceptions, ())

    def test_equality(self):
        # Create instances of AvrioAuthentication with different tokens
        token1 = "token1"
        token2 = "token2"
        auth1 = AvrioAuthentication(token1)
        auth2 = AvrioAuthentication(token2)
        auth3 = AvrioAuthentication(token1)

        # Assert that equality works correctly
        self.assertNotEqual(auth1, auth2)
        self.assertEqual(auth1, auth3)

    def test_equality_with_different_object(self):
        # Ensure equality fails with objects of different types
        self.assertNotEqual(self.auth, "Not an AvrioAuthentication object")


class TestBearerAuth(unittest.TestCase):
    def setUp(self):
        self.token = "dummy_token"
        self.auth = _BearerAuth(self.token)

    def test_init(self):
        # Assert that the token was set correctly
        self.assertEqual(self.auth.token, self.token)

    def test_call(self):
        # Create a mock PreparedRequest object
        request = MagicMock(spec=PreparedRequest)
        request.headers = {}

        # Call the __call__ method of _BearerAuth with the mock request
        result_request = self.auth(request)

        # Assert that the Authorization header was set correctly
        self.assertEqual(request.headers["Authorization"], "Bearer " + self.token)
        self.assertEqual(result_request, request)

    def test_call_with_existing_headers(self):
        # Test when the request already has headers
        request = MagicMock(spec=PreparedRequest)
        request.headers = {"Content-Type": "application/json"}

        result_request = self.auth(request)

        self.assertEqual(request.headers["Authorization"], "Bearer " + self.token)
        self.assertEqual(request.headers["Content-Type"], "application/json")
        self.assertEqual(result_request, request)

    def test_call_with_invalid_token(self):
        # Test behavior with an invalid or empty token
        empty_auth = _BearerAuth("")
        request = MagicMock(spec=PreparedRequest)
        request.headers = {}

        result_request = empty_auth(request)

        self.assertEqual(request.headers["Authorization"], "Bearer ")
        self.assertEqual(result_request, request)


class TestFullIntegration(unittest.TestCase):
    def test_integration_with_http_session(self):
        # Test AvrioAuthentication with a complete HTTP session
        token = "integration_test_token"
        auth = AvrioAuthentication(token)
        session = Session()

        updated_session = auth.set_http_session(session)

        # Ensure the session is updated with the correct authentication
        self.assertIsInstance(updated_session.auth, _BearerAuth)
        self.assertEqual(updated_session.auth.token, token)


if __name__ == "__main__":
    unittest.main()
