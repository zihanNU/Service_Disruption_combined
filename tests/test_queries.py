import unittest
from unittest.mock import Mock, patch
import engines
import types
import pandas as tpd
import datetime

class QueryTest(unittest.TestCase):

    now = datetime.datetime.now()

    def test_query_constructor(self):
        researchScienceConnStr = "research.science.conn.string"
        bazAnalyticsString = "baz.analytics.conn.string"
        bazReplConnString = "baz.repl.conn.str"
        
        queryEngine = self.get_queryengine(researchScienceConnStr, bazAnalyticsString, bazReplConnString)

        self.assertEqual(researchScienceConnStr, queryEngine.researchScienceConnectionString, "ResearchScienceConnString Should Equal value")
        self.assertEqual(bazAnalyticsString, queryEngine.bazookaAnalyticsConnString, "bazookaAnalyticsConnString Should Equal input value")
        self.assertEqual(bazReplConnString, queryEngine.bazookaReplConnString, "bazookaReplConnStr Should Equal input value")


    def test_query_get_carrier_histload_noresults_returns_zeros(self):
        carrierId = 12345
        startDate = self.now.strftime("%Y-%m-%d")
        endDate = (datetime.timedelta(1) + self.now).strftime("%Y-%m-%d")
        mockConnection = MockPyodbcConnection()

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['loadId'])
                mock_pandas_read_sql.return_value = my_df 
                actual = queryEngine.get_carrier_histload(carrierId, startDate, endDate)
            self.assertEqual(0, actual['flag'])
            self.assertEqual(0, actual['histload'])


    def test_query_get_carrier_histload_results_returns_data(self):
        carrierId = 12345
        startDate = self.now.strftime("%Y-%m-%d")
        endDate = (datetime.timedelta(1) + self.now).strftime("%Y-%m-%d")
        mockConnection = MockPyodbcConnection()        
        expected = {'loadId': 12345, 'origin_count': 3, 'dest_count': 5}

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['loadId', 'origin_count', 'dest_count'])
                my_df.loc[len(my_df)] = expected

                mock_pandas_read_sql.return_value = my_df 
                actual = queryEngine.get_carrier_histload(carrierId, startDate, endDate)
            self.assertEqual(1, actual['flag'])


    def test_query_get_truckinsurance(self):

        expectedCargoLimit = 123.45
        mockData = MockPyodbcDataSet(types.SimpleNamespace(CargoLimit=expectedCargoLimit))
        mockCursor = MockPyodbcCursor(mockData)
        mockConnection = MockPyodbcConnection(mockCursor)

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            actualCargoLimit = queryEngine.get_truckinsurance(1234)
            self.assertEqual(expectedCargoLimit, actualCargoLimit)


    def test_query_get_corridorinfo(self):

        mockConnection = MockPyodbcConnection()
        expected = {'loadId': 12345}

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['loadId'])
                my_df.loc[len(my_df)] = expected
                mock_pandas_read_sql.return_value = my_df 
                actual = queryEngine.get_corridorinfo()
            self.assertEqual(expected["loadId"], actual["loadId"][0])

    def get_queryengine(self, researchScienceConnStr = "research.science.conn.string", bazAnalyticsString = "baz.analytics.conn.string", bazookaReplConnStr = "baz.replication.conn.string"):
        return engines.QueryEngine(researchScienceConnStr, bazAnalyticsString, bazookaReplConnStr)
        


class MockPyodbcConnection:

    def __init__(self, mockPyodbcCursor = None):
        self.__mockPyodbcCursor = mockPyodbcCursor

    def cursor(self):
        return self.__mockPyodbcCursor


class MockPyodbcCursor:

    def __init__(self, mockDataSet = None):
        self.__mockDataSet = mockDataSet

    def execute(self, *args):
        return self.__mockDataSet


class MockPyodbcDataSet:

    def __init__(self, fetchOneResult):
        self.__fetchOneResult = fetchOneResult

    def fetchone(self):
        return self.__fetchOneResult
