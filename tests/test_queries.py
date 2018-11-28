import unittest
import engines

class QueryTest(unittest.TestCase):

    def test_query_constructor(self):
        #queryCollection = queries.QueryCollection("some string")
        #self.assertIsNotNone(queryCollection.researchScienceConnectionString)
        queryEngine = engines.QueryEngine("some string")
        self.assertIsNotNone(queryEngine.researchScienceConnectionString)