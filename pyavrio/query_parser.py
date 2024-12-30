from sql_metadata import Parser
import re

__all__ = ["QueryParser"]

class QueryParser:
    
    @staticmethod
    def parse_query(query, platform=None):
        """
        Parse and validate SQL query.
        
        Args:
            query (str): SQL query to parse
            platform (str, optional): Platform type for additional validation logic
                
        Returns:
            bool: True if query is valid, False otherwise
        """
        # Strip whitespace first to avoid unnecessary processing
        query = query.strip().lower()
        
        # Early return if empty query
        if not query:
            return False

        # Remove comments
        query = re.sub(r'(/\*.*?\*/|--.*?$)', '', query, flags=re.DOTALL | re.MULTILINE).strip()

        # Compatibility queries
        COMPATIBILITY_QUERIES = {'select 1', 'select 2', 'select 3'}
        
        # Check query type using startswith
        if query.startswith('select'):
            # Normalize whitespace more efficiently
            normalized_query = ' '.join(query.split())
            return normalized_query in COMPATIBILITY_QUERIES
        return query.startswith('alter')

    @staticmethod
    def remove_schema_from_query(_query, platform):
        """
        Remove schema from query for data products platform.
        
        Args:
            query (str): SQL query to process
            platform (str): Platform identifier
            
        Returns:
            str: Processed query with schema removed if applicable
        """
        parsed_query = Parser(_query)
        if platform == "data_products" and parsed_query.tables:
            for i, table in enumerate(parsed_query.tables):
                parts = table.split('.')
                if len(parts) == 2:
                    part_1 = parts[0]
                    part_2 = parts[1]

                    pattern_1 = re.compile(rf'"{re.escape(part_1)}"\."{re.escape(part_2)}"')
                    pattern_2 = re.compile(rf'"{re.escape(part_1)}"\.{re.escape(part_2)}')
                    pattern_3 = re.compile(rf'{re.escape(part_1)}\."{re.escape(part_2)}"')
                    pattern_4 = re.compile(rf'{re.escape(part_1)}\.{re.escape(part_2)}')

                    _query = pattern_1.sub(part_2, _query)
                    _query = pattern_2.sub(part_2, _query)
                    _query = pattern_3.sub(part_2, _query)
                    _query = pattern_4.sub(part_2, _query)
                    parsed_query.tables[i] = part_2
            return _query
        else:
            return _query
        
    