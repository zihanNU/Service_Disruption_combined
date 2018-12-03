import unittest
from config import Config
from xml.etree.ElementTree import Element, SubElement

def BuildConnectionStringElement():
    connStringElement = Element('connectionStrings')
    researchElement = SubElement(connStringElement, 'researchScience')
    researchElement.text = "research.connection.string"
    replicationElement = SubElement(connStringElement, 'bazookaRepl')
    replicationElement.text = 'replication.connection.string'
    analyticsElement = SubElement(connStringElement, 'bazookaAnalytics')
    analyticsElement.text = 'analytics.connection.string'
    return connStringElement


class ConfigTest(unittest.TestCase):

    def test_setConnectionStrings(self):
        element = BuildConnectionStringElement()
        config = Config(None, "1.0.0")

        researchScienceString = element.find('researchScience').text
        replicationString = element.find("bazookaRepl").text
        bazAnalyticsString = element.find('bazookaAnalytics').text

        config.setConnectionStrings(element)

        self.assertEqual(researchScienceString, config.researchScienceConnString, "ResearchScienceConnString Should Equal value")
        self.assertEqual(replicationString, config.bazookaReplConnString, "bazookaReplConnString Should Equal input value")
        self.assertEqual(bazAnalyticsString, config.bazookaAnalyticsConnString, "bazookaAnalyticsConnString Should Equal input value")


