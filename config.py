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

    def __init__(self, rootElement, version):
        self.initializeProperties()
        __rootElement = rootElement

        self.__versionNumber =  version

        if __rootElement != None:
            pathNode =  __rootElement.find('paths')
            self.setPaths(pathNode)

        if __rootElement != None:
            connNode = __rootElement.find('connectionStrings')
            self.setConnectionStrings(connNode)


    def initializeProperties(self):
        self.__modelPath = None
        self.__logPath = None
        self.__carrierDataPath = None
        self.__researchScienceConnString = None
        self.__bazookaReplConnString = None
        self.__bazookaAnalyticsConnString = None
        self.__versionNumber = None


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


    def setPaths(self, pathsNode):

        _paths_node = pathsNode
    
        _model_path = _paths_node.find('modelPath').text
        self.__modelPath = '' if _model_path is None else _model_path

        _log_path = _paths_node.find('logPath').text
        self.__logPath = '' if _log_path is None else _log_path

        _carrierDataPath = _paths_node.find('carrierDataPath').text
        self.__carrierDataPath = '' if _carrierDataPath is None else _carrierDataPath

    def setConnectionStrings(self, connStringsNode):
        _connStringsNode = connStringsNode
        
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



