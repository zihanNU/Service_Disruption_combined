import unittest
from unittest.mock import Mock, patch
import engines
import types

class QueryTest(unittest.TestCase):

    def test_query_constructor(self):
        queryEngine = engines.QueryEngine("researchScienceConnStr", "bazAnalyticsConnStr")
        self.assertEqual("researchScienceConnStr", queryEngine.researchScienceConnectionString, "ResearchScienceConnString Should Equal value")
        self.assertEqual("bazAnalyticsConnStr", queryEngine.bazookaAnalyticsConnString, "bazookaAnalyticsConnString Should Equal input value")


    def test_query_get_truckinsurance(self):

        expectedCargoLimit = 123.45
        mockData = MockPyodbcDataSet(types.SimpleNamespace(CargoLimit=expectedCargoLimit))
        mockCursor = MockPyodbcCursor(mockData)
        mockConnection = MockPyodbcConnection(mockCursor)

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = engines.QueryEngine("researchScienceConnStr", "bazAnalyticsConnStr")
            actualCargoLimit = queryEngine.get_truckinsurance(1234)
            self.assertEqual(expectedCargoLimit, actualCargoLimit)

class MockPyodbcConnection:

    def __init__(self, mockPyodbcCursor):
        self.__mockPyodbcCursor = mockPyodbcCursor

    def cursor(self):
        return self.__mockPyodbcCursor

class MockPyodbcCursor:

    def __init__(self, mockDataSet):
        self.__mockDataSet = mockDataSet

    def execute(self, *args):
        return self.__mockDataSet

class MockPyodbcDataSet:

    def __init__(self, fetchOneResult):
        self.__fetchOneResult = fetchOneResult

    def fetchone(self):
        return self.__fetchOneResult
