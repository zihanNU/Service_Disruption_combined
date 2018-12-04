import unittest
from unittest.mock import Mock, patch
import engines
import types
import pandas as tpd
import datetime


_researchScienceConnectionString = "research.science.conn.string"
_bazAnalyticsConnectionString = "baz.analytics.conn.string"
_bazookaReplConnStr = "baz.replication.conn.string"


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
                self.assert_proper_connection(mock_connect, _researchScienceConnectionString)
            self.assertEqual(1, actual['flag'])


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
                self.assert_proper_connection(mock_connect, _researchScienceConnectionString)
            self.assertEqual(expected["loadId"], actual["loadId"][0])


    def test_query_get_truckinsurance(self):

        expectedCargoLimit = 123.45
        mockData = MockPyodbcDataSet(types.SimpleNamespace(CargoLimit=expectedCargoLimit))
        mockCursor = MockPyodbcCursor(mockData)
        mockConnection = MockPyodbcConnection(mockCursor)

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            actualCargoLimit = queryEngine.get_truckinsurance(1234)
            self.assert_proper_connection(mock_connect, _bazAnalyticsConnectionString)
            self.assertEqual(expectedCargoLimit, actualCargoLimit)


    def test_get_trucksearch(self):
        mockConnection = MockPyodbcConnection()

        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['carrierID', 'originCluster', 'destinationCluster'])
                my_df.loc[0] = {"carrierID": 5213, "originCluster": "Nashville Region", "destinationCluster" : "South GA Region"}
                my_df.loc[1] = {"carrierID": 5213, "originCluster": "Nashville Region", "destinationCluster" : "South GA Region"}
                mock_pandas_read_sql.return_value = my_df
                actual = queryEngine.get_trucksearch(12345)
                
                self.assert_proper_connection(mock_connect, _researchScienceConnectionString)
                self.assertEqual(1, len(actual.index), "expected the duplicate to be dropped, and to have 1 record")
                self.assertEqual(5213, actual["carrierID"][0], "expected the proper carrierID")


    def test_get_newload(self):
        mockConnection = MockPyodbcConnection()
        with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = self.get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['loadID'])
                my_df.loc[0] = {"loadID": 1234567890}
                mock_pandas_read_sql.return_value = my_df
                actual = queryEngine.get_newload('11/23/2018', '11/23/2018')
                self.assert_proper_connection(mock_connect, _bazookaReplConnStr)
                self.assertEqual(1234567890, actual["loadID"][0], "Expected proper loadID returned")

    def assert_proper_connection(self, mockConnect, expectedConnectionString):
        """Tests for one call to .connect on the mock connection object, and the proper connection string"""
        self.assertTrue(mockConnect.call_count == 1, "Expected one call to mock connection")
        self.assertTrue(mockConnect.call_args[0][0] == expectedConnectionString, "Expected mock connection called with proper connection string")


    def get_queryengine(self, researchScienceConnStr = _researchScienceConnectionString, 
                              bazAnalyticsString = _bazAnalyticsConnectionString, 
                              bazookaReplConnStr = _bazookaReplConnStr):
        """Helper method to instantiate the query engine"""
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
