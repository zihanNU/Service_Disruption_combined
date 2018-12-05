from unittest.mock import Mock, patch
import engines
import types
import pandas as tpd
import datetime


_researchScienceConnectionString = "research.science.conn.string"
_bazAnalyticsConnectionString = "baz.analytics.conn.string"
_bazookaReplConnStr = "baz.replication.conn.string"
_now = datetime.datetime.now()

def test_query_constructor():
    researchScienceConnStr = "research.science.conn.string"
    bazAnalyticsString = "baz.analytics.conn.string"
    bazReplConnString = "baz.repl.conn.str"
    
    queryEngine = get_queryengine(researchSciString = researchScienceConnStr, bazAnalyticsString = bazAnalyticsString, bazookaReplConnStr = bazReplConnString)

    assert researchScienceConnStr == queryEngine.researchScienceConnectionString
    assert bazAnalyticsString == queryEngine.bazookaAnalyticsConnString
    assert bazReplConnString == queryEngine.bazookaReplConnString


def test_query_get_carrier_histload_noresults_returns_zeros():
    carrierId = 12345
    mockConnection = MockPyodbcConnection()

    with patch("pyodbc.connect") as mock_connect:
        mock_connect.return_value = mockConnection
        queryEngine = get_queryengine()
        with patch("pandas.read_sql") as mock_pandas_read_sql:
            my_df = tpd.DataFrame(columns=['loadId'])
            mock_pandas_read_sql.return_value = my_df 
            actual = queryEngine.get_carrier_histload(carrierId)
        assert 0 == actual['flag']
        assert 0 == actual['histload']


def test_query_get_carrier_histload_results_returns_data():
    carrierId = 12345
    mockConnection = MockPyodbcConnection()        
    expected = {'loadId': 12345, 'origin_count': 3, 'dest_count': 5}

    with patch("pyodbc.connect") as mock_connect:
        mock_connect.return_value = mockConnection
        queryEngine = get_queryengine()
        with patch("pandas.read_sql") as mock_pandas_read_sql:
            my_df = tpd.DataFrame(columns=['loadId', 'origin_count', 'dest_count'])
            my_df.loc[len(my_df)] = expected

            mock_pandas_read_sql.return_value = my_df 
            actual = queryEngine.get_carrier_histload(carrierId)
            assert_proper_connection(mock_connect, _researchScienceConnectionString)
        assert 1 == actual['flag']


def test_query_get_corridorinfo():

    mockConnection = MockPyodbcConnection()
    expected = {'loadId': 12345}

    with patch("pyodbc.connect") as mock_connect:
        mock_connect.return_value = mockConnection
        queryEngine = get_queryengine()
        with patch("pandas.read_sql") as mock_pandas_read_sql:
            my_df = tpd.DataFrame(columns=['loadId'])
            my_df.loc[len(my_df)] = expected
            mock_pandas_read_sql.return_value = my_df 
            actual = queryEngine.get_corridorinfo()
            assert_proper_connection(mock_connect, _researchScienceConnectionString)
        assert expected["loadId"] == actual["loadId"][0]


def test_query_get_truckinsurance():

    expectedCargoLimit = 123.45
    mockData = MockPyodbcDataSet(types.SimpleNamespace(CargoLimit=expectedCargoLimit))
    mockCursor = MockPyodbcCursor(mockData)
    mockConnection = MockPyodbcConnection(mockCursor)

    with patch("pyodbc.connect") as mock_connect:
        mock_connect.return_value = mockConnection
        queryEngine = get_queryengine()
        actualCargoLimit = queryEngine.get_truckinsurance(1234)
        assert_proper_connection(mock_connect, _bazAnalyticsConnectionString)
        assert expectedCargoLimit == actualCargoLimit


def test_get_trucksearch():
    mockConnection = MockPyodbcConnection()

    with patch("pyodbc.connect") as mock_connect:
        mock_connect.return_value = mockConnection
        queryEngine = get_queryengine()
        with patch("pandas.read_sql") as mock_pandas_read_sql:
            my_df = tpd.DataFrame(columns=['carrierID', 'originCluster', 'destinationCluster'])
            my_df.loc[0] = {"carrierID": 5213, "originCluster": "Nashville Region", "destinationCluster" : "South GA Region"}
            my_df.loc[1] = {"carrierID": 5213, "originCluster": "Nashville Region", "destinationCluster" : "South GA Region"}
            mock_pandas_read_sql.return_value = my_df
            actual = queryEngine.get_trucksearch(12345)
            
            assert_proper_connection(mock_connect, _researchScienceConnectionString)
            assert 1 == len(actual.index)
            assert 5213 == actual["carrierID"][0]


def test_get_newload_has_carrierlatlong():
    mockConnection = MockPyodbcConnection()

    latitude = 44.975
    longitude = -93.268
    cargolimit = 75000

    with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:
                my_df = tpd.DataFrame(columns=['loadID'])
                my_df.loc[0] = {"loadID": 1234567890}
                mock_pandas_read_sql.return_value = my_df          
                actual = queryEngine.get_newload(latitude, longitude, cargolimit)
                assert_proper_connection(mock_connect, _researchScienceConnectionString)
                assert 1234567890 == actual["loadID"][0]
                assert "@carrierlon" in mock_pandas_read_sql.call_args[1]["sql"]


def test_get_newload_missing_carrierlatlong():
    mockConnection = MockPyodbcConnection()

    latitude = None
    longitude = None
    cargolimit = 75000

    with patch("pyodbc.connect") as mock_connect:
            mock_connect.return_value = mockConnection
            queryEngine = get_queryengine()
            with patch("pandas.read_sql") as mock_pandas_read_sql:    
                queryEngine.get_newload(latitude, longitude, cargolimit)
                assert "@carrierlon" not in mock_pandas_read_sql.call_args[0][0]
                

def assert_proper_connection(mockConnect, expectedConnectionString):
    """Tests for one call to .connect on the mock connection object, and the proper connection string"""
    assert mockConnect.call_count == 1
    assert mockConnect.call_args[0][0] == expectedConnectionString

def get_queryengine(researchSciString = _researchScienceConnectionString, 
                            bazAnalyticsString = _bazAnalyticsConnectionString, 
                            bazookaReplConnStr = _bazookaReplConnStr):
    """Helper method to instantiate the query engine"""
    return engines.QueryEngine(researchSciString, bazAnalyticsString, bazookaReplConnStr)
    


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
