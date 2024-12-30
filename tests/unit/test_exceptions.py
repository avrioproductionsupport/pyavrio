import unittest
from pyavrio.exceptions import (
    Error, Warning, InterfaceError, DatabaseError, InternalError, OperationalError,
    ProgrammingError, IntegrityError, DataError, NotSupportedError, TrinoAuthError,
    TrinoConnectionError, TrinoDataError, TrinoQueryError, TrinoExternalError,
    TrinoInternalError, TrinoUserError, HttpError, Http502Error, Http503Error, Http504Error
)


class TestExceptions(unittest.TestCase):

    def test_base_exceptions(self):
        with self.assertRaises(Error):
            raise Error()

        with self.assertRaises(Warning):
            raise Warning()

        with self.assertRaises(InterfaceError):
            raise InterfaceError()

    def test_database_errors(self):
        with self.assertRaises(DatabaseError):
            raise DatabaseError()

        with self.assertRaises(InternalError):
            raise InternalError()

        with self.assertRaises(OperationalError):
            raise OperationalError()

        with self.assertRaises(ProgrammingError):
            raise ProgrammingError()

        with self.assertRaises(IntegrityError):
            raise IntegrityError()

        with self.assertRaises(DataError):
            raise DataError()

        with self.assertRaises(NotSupportedError):
            raise NotSupportedError()

    def test_trino_errors(self):
        with self.assertRaises(TrinoAuthError):
            raise TrinoAuthError()

        with self.assertRaises(TrinoConnectionError):
            raise TrinoConnectionError()

        with self.assertRaises(TrinoDataError):
            raise TrinoDataError()

        with self.assertRaises(TrinoQueryError):
            raise TrinoQueryError({})

        with self.assertRaises(TrinoExternalError):
            raise TrinoExternalError({})

        with self.assertRaises(TrinoInternalError):
            raise TrinoInternalError({})

        with self.assertRaises(TrinoUserError):
            raise TrinoUserError({})

    def test_http_errors(self):
        with self.assertRaises(HttpError):
            raise HttpError()

        with self.assertRaises(Http502Error):
            raise Http502Error()

        with self.assertRaises(Http503Error):
            raise Http503Error()

        with self.assertRaises(Http504Error):
            raise Http504Error()

class TestTrinoQueryError(unittest.TestCase):
    def test_error_properties(self):
        error_dict = {
            "errorCode": 500,
            "errorName": "InternalError",
            "errorType": "Server Error",
            "failureInfo": {
                "type": "RuntimeException"
            },
            "message": "An internal server error occurred.",
            "errorLocation": {
                "lineNumber": 10,
                "columnNumber": 5
            }
        }
        query_id = "12345"
        trino_error = TrinoQueryError(error=error_dict, query_id=query_id)

        self.assertEqual(trino_error.error_code, 500)
        self.assertEqual(trino_error.error_name, "InternalError")
        self.assertEqual(trino_error.error_type, "Server Error")
        self.assertEqual(trino_error.error_exception, "RuntimeException")
        self.assertEqual(trino_error.message, "An internal server error occurred.")
        self.assertEqual(trino_error.error_location, (10, 5))
        self.assertEqual(trino_error.query_id, "12345")

    def test_default_message(self):
        error_dict = {"errorCode": 404}
        trino_error = TrinoQueryError(error=error_dict)

        self.assertEqual(trino_error.message, "Trino did not return an error message")

if __name__ == "__main__":
    unittest.main()
