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


def test_set_connection_strings():
    element = BuildConnectionStringElement()
    config = Config(None, "1.0.0")

    researchScienceString = element.find('researchScience').text
    replicationString = element.find("bazookaRepl").text
    bazAnalyticsString = element.find('bazookaAnalytics').text

    config.setConnectionStrings(element)

    assert researchScienceString == config.researchScienceConnString
    assert replicationString == config.bazookaReplConnString
    assert bazAnalyticsString == config.bazookaAnalyticsConnString



