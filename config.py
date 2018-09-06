import os
import xml.etree.ElementTree

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(DIR_PATH, 'app_recommender.config')

try:
    ROOT_ELEMENT = xml.etree.ElementTree.parse(CONFIG_FILE).getroot()
except Exception as ex:
    print('Handled Error in xml.etree.ElementTree.parse({}).getroot():{}'.format(CONFIG_FILE, str(ex)))
    raise ex

class Config(object):
    #DEBUG = False
    #TESTING = False

    def __init__(self, rootElement):
        self.initializeProperties()
        self.__rootElement = rootElement
        self.__connectionString = ROOT_ELEMENT.find('connectionStrings').text

        self.setPaths()
        self.setConnectionStrings()


    def initializeProperties(self):
        self.__rootElement = None
        self.__connectionString = None
        self.__modelPath = None
        self.__logPath = None
        self.__carrierDataPath = None
        self.__dataScienceConnString = None
        self.__bazookaReplConnString = None
        self.__bazookaAnalyticsConnString = None

    @property
    def rootElement(self):
        return self.__rootElement
    # @rootElement.setter
    # def rootElement(self, value):
    #     self._rootElement = value

    @property
    def connectionString(self):
        return self.__connectionString
    # @connectionString.setter
    # def connectionString(self, value):
    #     self._connectionString = value

    @property
    def modelPath(self):
        return self.__modelPath
    # @modelPath.setter
    # def modelPath(self, value):
    #     self._modelPath = value

    @property 
    def logPath(self):
        return self.__logPath
    # @logPath.setter
    # def logPath(self, value):
    #     self._logPath = value

    @property
    def carrierDataPath(self):
        return self.__carrierDataPath

    @property
    def dataScienceConnString(self):
        return self.__dataScienceConnString

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
        
        _dataScienceConnString = _connStringsNode.find('dataScience').text
        _bazookaReplConnString = _connStringsNode.find('bazookaRepl').text
        _bazookaAnalyticsConnString = _connStringsNode.find('bazookaAnalytics').text
        
        self.__dataScienceConnString = '' if _dataScienceConnString is None else _dataScienceConnString
        self.__bazookaReplConnString = '' if _bazookaReplConnString is None else _bazookaReplConnString
        self.__bazookaAnalyticsConnString = '' if _bazookaAnalyticsConnString is None else _bazookaAnalyticsConnString
    
try:
    CONFIG = Config(ROOT_ELEMENT)
except Exception as ex:
    print('Handled Error in Config():{}'.format(str(ex)))
    raise ex



