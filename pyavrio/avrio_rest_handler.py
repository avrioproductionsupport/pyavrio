import json
from urllib.parse import quote
from typing import Optional, Dict, Any, List
import requests
from pyavrio.sqlalchemy import datatype
from .endpoints import AvrioEndpoints
from .exceptions import AvrioAuthenticationError, AvrioRequestError

__all__ = ["AvrioHTTPHandler"]

class AvrioHTTPHandler:

    def __init__(self, base_url, access_token):
        self._base_url = base_url
        self._access_token = access_token
        
    def _get(self,  endpoint, params=None):
        """
        Perform a GET request to the specified endpoint with optional parameters.

        This method constructs a URL with the given endpoint and parameters, then sends a GET request
        to that URL with the provided access token in the headers.

        :param endpoint: The endpoint to send the GET request to.
        :param params: Optional. A dictionary containing query parameters.
        :return: The response object returned by the GET request.
        """
        encoded_params = "&".join([f"{key}={quote(str(value))}" for key, value in params.items()])
        url_with_params = f"{self._base_url}{endpoint}?{encoded_params}"
        headers = {'Authorization': 'Bearer '+self._access_token}
        response = requests.get(url=url_with_params,headers=headers)
        return response
    
    def _get_modified_query(self, email, sql,access_token, catalog):
        """
        Get the modified SQL query for a given email and input SQL.

        This method sends a POST request to the specified endpoint with the provided email,
        input SQL, and access token in the request body. It returns the response object.

        :param email: The email address associated with the modified query.
        :param sql: The input SQL query to be modified.
        :param access_token: The access token for authorization.
        :return: The response object returned by the POST request.
        """
        payload = {"inputQuerySql": sql, "email": email, "catalog": catalog}
        endpoint = AvrioEndpoints.MODIFIED_QUERY
        url_with_params = f"{self._base_url}{endpoint}"
        headers = {'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json'}

        try:
            response = requests.post(url=url_with_params, headers=headers, json=payload)
            return response
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to get response: {str(e)}")

       
            
    def _generate_token(self, username, password, host) -> str:
        """
        Function to generate authentication token by calling an Avrio API.
        
        This function sends a request to the Avrio API with provided username and password to
        obtain an authentication token.
        
        Parameters:
            username (str): The username for authentication.
            password (str): The password for authentication.
            host (str): The host URL of the Avrio API.
        
        Returns:
            str: The authentication token obtained from the Avrio API.
        """
        payload = {"email": username, "password": password,"host":host}
        url = AvrioEndpoints.IAM_SIGNIN
        url_with_params = f"{self._base_url}{url}"
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url=url_with_params, headers=headers, json=payload)
            response.raise_for_status()
            token = response.json().get("accessToken")
            if not token:
                raise AvrioAuthenticationError("No access token in response")
            return token
        except requests.exceptions.RequestException as e:
            raise AvrioAuthenticationError(f"Authentication failed: {str(e)}")
        
    def _get_catalogs_dp(self, userEmail, token):
        """
        Function to retrieve data product catalogs.
        
        This function makes a request to the specified host with provided user email and token
        to fetch data product catalogs.
        
        Parameters:
            userEmail (str): The email address of the user.
            token (str): The authentication token for accessing the data product catalogs.
        
        Returns:
            list: A list of domain names extracted from the Avrio platform.
        """

        url = AvrioEndpoints.DATASETS_BASE.format(email=userEmail)
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [item['domain'] for item in data]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch catalogs: {str(e)}")
       
    def _get_schemas_dp(self, userEmail, domain, token):
        """
        Function to retrieve schemas of a specified domain from the Avrio Data Product platform.
        
        This function makes a request to the specified host with provided user email, domain, and token
        to fetch schemas of the specified domain from the Avrio Data Product platform.
        
        Parameters:
            userEmail (str): The email address of the user.
            domain (str): The domain for which schemas are to be retrieved.
            token (str): The authentication token for accessing the Avrio platform.
        
        Returns:
            list: A list of schemas belonging to the specified domain.
        """
        url = AvrioEndpoints.DATASETS_DOMAIN.format(email=userEmail, domain=domain)
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            schemas = [item['domain'] for item in data]
            return schemas
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching schemas: {e}")
            return []

    def _get_schemas_dp_1(self, email, token, params):
        url = AvrioEndpoints.PYTHON_SCHEMAS.format(email=email)
        encoded_params = "&".join([f"{key}={quote(str(value))}" for key, value in params.items()])
        url_with_params = f"{self._base_url}{url}?{encoded_params}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "data" not in data:
                raise AvrioRequestError("No data field in response")
            return data["data"]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch schemas: {str(e)}")
        

    def _get_tables_dp(self, userEmail, domainName, token, subDomainName):
        """
        Function to retrieve data product names from the Avrio Data Product platform.
        
        This function makes a request to the specified host with provided user email, domain name, token, and subdomain name
        to fetch data product names from the Avrio Data Product platform.
        
        Parameters:
            userEmail (str): The email address of the user.
            domainName (str): The name of the domain for which data product names are to be retrieved.
            token (str): The authentication token for accessing the Avrio platform.
            subDomainName (str): The name of the subdomain within the specified domain.
        
        Returns:
            list: A list of data product names belonging to the specified domain and subdomain.
        """
        
        try:
            # Format the endpoint with the provided parameters
            endpoint = AvrioEndpoints.DATASETS_SUBDOMAIN.format(
                email=quote(userEmail),
                domain=quote(domainName),
                subdomain=quote(subDomainName)
            )
            
            # Construct the full URL
            url = f"{self._base_url}{endpoint}"
            
            # Set up headers with authentication token
            headers = {"Authorization": f"Bearer {token}"}
            
            # Make the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse and return the data
            data = response.json()
            tables = []
            for key in data:
                tables.extend(data[key])
            return tables
            
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch tables: {str(e)}")
        except (KeyError, TypeError) as e:
            raise AvrioRequestError(f"Invalid response format: {str(e)}")

    def _get_tables_dp_1(self, email: str, token: str,  params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Function to retrieve tables from the Avrio Data Product platform.
        
        This function makes a request to the specified host with provided user email and token
        to fetch tables from the Avrio Data Product platform.
        
        Parameters:
            email (str): The email address of the user.
            token (str): The authentication token for accessing the platform.
            params (Optional[Dict[str, Any]]): Optional query parameters for the request.
        
        Returns:
            List[Dict[str, Any]]: List of tables data from the platform.
        """
        url = AvrioEndpoints.PYTHON_TABLES.format(email=email)
        
        if params:
            encoded_params = "&".join([f"{key}={quote(str(value))}" for key, value in params.items()])
            url_with_params = f"{self._base_url}{url}?{encoded_params}"
        else:
            url_with_params = f"{self._base_url}{url}"
            
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["data"]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch tables: {str(e)}")

    
    def _get_columns_dp(self, userEmail, token, dataproduct):
        """
        Function to retrieve columns of a data product from the Avrio Data Product platform and return as a dictionary.
        
        This function makes a request to the specified host with provided user email, token, and data product
        to fetch columns from the Avrio Data Product platform.
        
        Parameters:
            userEmail (str): The email address of the user.
            token (str): The authentication token for accessing the Avrio platform.
            dataproduct (str): The name of the data product for which columns are to be retrieved.
        
        Returns:
            list: A list of dictionary mapping column names to their types.
        """
        
        url = AvrioEndpoints.DATASETS_COLUMNS.format(email=userEmail, dataproduct=dataproduct)
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            columns = data.get('columns', [])
            return [
                {'name': column.get('colName'), 
                'type': datatype.parse_sqltype(column.get('colType')), 
                'nullable': 'YES'}
                for column in columns
                if column.get('colName') and column.get('colType')
            ]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch columns: {str(e)}")
    
    def _get_catalogs_ds(self, userEmail, token):
        """
        Function to retrieve catalogs of data sources from the Avrio platform.
        
        This function makes a request to the specified host with provided user email and token
        to fetch catalogs of data sources.
        
        Parameters:
            userEmail (str): The email address of the user.
            token (str): The authentication token for accessing the Avrio platform.
        
        Returns:
            list: A list of catalogs of data sources.
        """

        url = AvrioEndpoints.JDBC_DATASOURCES.format(email=userEmail)
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [item['name'] for item in data]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch catalogs: {str(e)}")
        
    def _get_schemas_ds(self, emailAddress, datasource, token):
        """
        Function to retrieve schemas of a specified datasource from the Avrio Data Source platform.
        
        This function makes a request to the specified host with provided user email, datasource (catalog), and token
        to fetch schemas of the specified datasource from the Avrio Data Source platform.
        
        Parameters:
            emailAddress (str): The email address of the user.
            datasource (str): The datasource (catalog) for which schemas are to be retrieved.
            token (str): The authentication token for accessing the Avrio platform.
        
        Returns:
            list: A list of schemas belonging to the specified datasource (catalog).
        """
        url = AvrioEndpoints.JDBC_SCHEMAS.format(email=emailAddress, datasource=datasource)
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [schema['schemaName'] for schema in data]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch schemas: {str(e)}")
 
    def _get_tables_ds(self, emailAddress, catalog, token, schema):
        """
        Function to retrieve tables from the Avrio Data Source platform.
        
        This function makes a request to the specified host with provided user email, catalog, token, and schema
        to fetch tables from the Avrio Data Source platform.
        
        Parameters:
            emailAddress (str): The email address of the user.
            catalog (str): The catalog for which tables are to be retrieved.
            token (str): The authentication token for accessing the Avrio platform.
            schema (str): The schema within the specified catalog.
        
        Returns:
            list: A list of tables belonging to the specified catalog and schema.
        """
        
        url = AvrioEndpoints.JDBC_TABLES.format(
            email=emailAddress,
            catalog=catalog,
            schema=schema
        )
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [table['tableName'] for table in data]
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch tables: {str(e)}")

    def _get_columns_ds(self, emailAddress, token, catalog, schema, table):
        """
        Function to retrieve columns from the Avrio Data Source platform.
        
        This function makes a request to the specified host with provided user email, token, catalog, schema, and table
        to fetch columns from the Avrio Data Source platform.
        
        Parameters:
            emailAddress (str): The email address of the user.
            token (str): The authentication token for accessing the Avrio platform.
            catalog (str): The catalog containing the specified schema and table.
            schema (str): The schema containing the specified table.
            table (str): The table for which columns are to be retrieved.
        
        Returns:
            list: A list of dictionaries containing information about columns, including their names and data types.
        """
        url = AvrioEndpoints.DATASOURCE_COLUMNS.format(
            email=emailAddress,
            catalog=catalog,
            schema=schema,
            table=table
            )
        url_with_params = f"{self._base_url}{url}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url_with_params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            columns_info = []
            for column_data in data:
                column_name = column_data.get('name')
                data_type = column_data.get('dataType')
                if column_name and data_type:
                    column_info = {
                        'name': column_name, 
                        'type': data_type, 
                        'nullable': 'YES'
                    }
                    columns_info.append(column_info)
            return columns_info
            
        except requests.exceptions.RequestException as e:
            raise AvrioRequestError(f"Failed to fetch columns: {str(e)}")
