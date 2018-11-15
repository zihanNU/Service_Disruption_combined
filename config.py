import os
import xml.etree.ElementTree

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(DIR_PATH, 'app_recommender.config')
VERSION_FILE = open('MatchingResearch.Api.version', 'r', encoding='UTF-16')

try:
    ROOT_ELEMENT = xml.etree.ElementTree.parse(CONFIG_FILE).getroot()
except Exception as ex:
    print('Handled Error in xml.etree.ElementTree.parse({}).getroot():{}'.format(CONFIG_FILE, str(ex)))
    raise ex

class Config(object):
    #DEBUG = False
    #TESTING = False

    def __init__(self, rootElement, version):
        self.initializeProperties()
        self.__rootElement = rootElement

        self.__versionNumber =  version

        self.setPaths()
        self.setConnectionStrings()


    def initializeProperties(self):
        self.__rootElement = None
        self.__modelPath = None
        self.__logPath = None
        self.__carrierDataPath = None
        self.__researchScienceConnString = None
        self.__bazookaReplConnString = None
        self.__bazookaAnalyticsConnString = None
        self.__versionNumber = None

    @property
    def rootElement(self):
        return self.__rootElement
    # @rootElement.setter
    # def rootElement(self, value):
    #     self._rootElement = value

    @property
    def versionNumber(self):
        return self.__versionNumber

    @property
    def modelPath(self):
        return self.__modelPath

    @property 
    def logPath(self):
        return self.__logPath

    @property
    def carrierDataPath(self):
        return self.__carrierDataPath

    @property
    def researchScienceConnString(self):
        return self.__researchScienceConnString

    @property
    def bazookaReplConnString(self):
        return self.__bazookaReplConnString

    @property
    def bazookaAnalyticsConnString(self):
        return self.__bazookaAnalyticsConnString        


    def setPaths(self):
        _paths_node = self.rootElement.find('paths')
    
        _model_path = _paths_node.find('modelPath').text
        self.__modelPath = '' if _model_path is None else _model_path

        _log_path = _paths_node.find('logPath').text
        self.__logPath = '' if _log_path is None else _log_path

        _carrierDataPath = _paths_node.find('carrierDataPath').text
        self.__carrierDataPath = '' if _carrierDataPath is None else _carrierDataPath

    def setConnectionStrings(self):
        _connStringsNode = self.rootElement.find('connectionStrings')
        
        _researchScienceConnString = _connStringsNode.find('researchScience').text
        _bazookaReplConnString = _connStringsNode.find('bazookaRepl').text
        _bazookaAnalyticsConnString = _connStringsNode.find('bazookaAnalytics').text
        
        self.__researchScienceConnString = '' if _researchScienceConnString is None else _researchScienceConnString
        self.__bazookaReplConnString = '' if _bazookaReplConnString is None else _bazookaReplConnString
        self.__bazookaAnalyticsConnString = '' if _bazookaAnalyticsConnString is None else _bazookaAnalyticsConnString
    
try:
    CONFIG = Config(ROOT_ELEMENT, VERSION_FILE.read().strip())
except Exception as ex:
    print('Handled Error in Config():{}'.format(str(ex)))
    raise ex



