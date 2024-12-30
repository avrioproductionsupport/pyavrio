import unittest
from unittest.mock import patch, MagicMock
from pyavrio.avrio_rest_handler import AvrioHTTPHandler  
from pyavrio.endpoints import AvrioEndpoints


class TestAvrioHTTPHandler(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://example.com'
        self.access_token = 'sample_token'
        self.handler = AvrioHTTPHandler(self.base_url, self.access_token)

    @patch('requests.get')
    def test_get(self, mock_get):
        endpoint = '/test-endpoint'
        params = {'param1': 'value1', 'param2': 'value2'}
        expected_url = f"{self.base_url}{endpoint}?param1=value1&param2=value2"
        expected_headers = {'Authorization': 'Bearer ' + self.access_token}
        expected_response = MagicMock()

        mock_get.return_value = expected_response

        response = self.handler._get(endpoint, params)

        mock_get.assert_called_once_with(url=expected_url, headers=expected_headers)
        self.assertEqual(response, expected_response)

    @patch("requests.post")
    def test_get_modified_query(self, mock_post):
        # Sample input data
        email = "test@example.com"
        sql = "SELECT * FROM users"
        access_token = "dummy_access_token"
        catalog = "default"

        # Expected values
        expected_url = f"{self.base_url}/query-engine/dataDiscovery/getModifiedQuery/v2"
        expected_payload = {"inputQuerySql": sql, "email": email, "catalog": catalog}
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Mock the response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "modified_query"}
        mock_post.return_value = mock_response

        # Call the method
        response = self.handler._get_modified_query(email, sql, access_token, catalog) 

        # Assertions
        mock_post.assert_called_once_with(
            url=expected_url, headers=expected_headers, json=expected_payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "data": "modified_query"})

    @patch("requests.post")
    def test_get_modified_query_failure(self, mock_post):
        # Sample input data
        email = "test@example.com"
        sql = "SELECT * FROM invalid_table"
        access_token = "dummy_access_token"
        catalog = "default"
        # Mock a failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"success": False, "error": "Invalid query"}
        mock_post.return_value = mock_response

        # Call the method
        response = self.handler._get_modified_query(email, sql, access_token, catalog) 

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"success": False, "error": "Invalid query"})

        mock_post.assert_called_once()

    @patch('requests.post')
    def test_generate_token(self, mock_post):
        username = 'test_user'
        password = 'test_password'
        host = 'example.com'
        expected_payload = {"email": username, "password": password, "host": host}
        expected_url = f"https://{host}/iam/security/signin"
        expected_headers = {'Content-Type': 'application/json'}
        expected_response = MagicMock()
        expected_response.status_code = 200
        expected_response.json.return_value = {'accessToken': 'sample_token'}

        mock_post.return_value = expected_response

        token = self.handler._generate_token(username, password, host)

        mock_post.assert_called_once_with(url=expected_url, headers=expected_headers, json=expected_payload)
        self.assertEqual(token, 'sample_token')
    
    @patch('requests.get')
    def test_get_catalogs_dp(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'domain': 'domain1'}, {'domain': 'domain2'}]
        mock_get.return_value = mock_response

        result = self.handler._get_catalogs_dp('test@example.com', 'token') 

        self.assertEqual(result, ['domain1', 'domain2'])

    @patch('requests.get')
    def test_get_schemas_dp(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'domain': 'domain1'}, {'domain': 'domain2'}]
        mock_get.return_value = mock_response

        result = self.handler._get_schemas_dp('test@example.com', 'example_domain', 'token') 

        self.assertEqual(result, ['domain1', 'domain2'])

    @patch('requests.get')
    def test_get_tables_dp(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'key1': ['table1', 'table2'], 'key2': ['table3']}
        mock_get.return_value = mock_response

        result = self.handler._get_tables_dp('test@example.com', 'example_domain', 'token', 'subdomain') 

        self.assertEqual(result, ['table1', 'table2', 'table3'])
   
    @patch('pyavrio.avrio_rest_handler.requests.get')
    def test_get_schemas_ds(self, mock_get):
        # Mocking the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'schemaName': 'Schema1'}, {'schemaName': 'Schema2'}]
        mock_get.return_value = mock_response

        # Calling the function with mock parameters
        schemas = self.handler._get_schemas_ds('user@example.com', 'Catalog1', 'token123') 

        # Asserting the returned value
        self.assertEqual(schemas, ['Schema1', 'Schema2'])

    @patch('pyavrio.avrio_rest_handler.requests.get')
    def test_get_tables_ds(self, mock_get):
        # Mocking the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'tableName': 'Table1'}, {'tableName': 'Table2'}]
        mock_get.return_value = mock_response

        # Calling the function with mock parameters
        tables = self.handler._get_tables_ds('user@example.com', 'Catalog1', 'token123', 'Schema1')  

        # Asserting the returned value
        self.assertEqual(tables, ['Table1', 'Table2'])

if __name__ == '__main__':
    unittest.main()
