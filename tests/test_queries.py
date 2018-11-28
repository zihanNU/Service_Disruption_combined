import unittest
import engines

class QueryTest(unittest.TestCase):

    def test_query_constructor(self):
        queryEngine = engines.QueryEngine("researchScienceConnStr", "bazAnalyticsConnStr")
        self.assertEqual("researchScienceConnStr", queryEngine.researchScienceConnectionString, "ResearchScienceConnString Should Equal value")
        self.assertEqual("bazAnalyticsConnStr", queryEngine.bazookaAnalyticsConnString, "bazookaAnalyticsConnString Should Equal input value")