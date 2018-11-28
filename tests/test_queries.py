import unittest
import engines

class QueryTest(unittest.TestCase):

    def test_query_constructor(self):
        queryEngine = engines.QueryEngine("some string")
        self.assertIsNotNone(queryEngine.researchScienceConnectionString)