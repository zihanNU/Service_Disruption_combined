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


    def initializeProperties(self):
        self.__rootElement = None
        self.__connectionString = None
        self.__modelPath = None
        self.__logPath = None

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


    def setPaths(self):
        _paths_node = self.rootElement.find('paths')
    
        _model_path = _paths_node.find('modelPath').text
        self.__modelPath = '' if _model_path is None else _model_path

        _log_path = _paths_node.find('logPath').text
        self.__logPath = '' if _log_path is None else _log_path

        #print("PATHS!!!!")
        #print("_paths:{}".format(_paths))
        #print("_model_path:{}".format(_model_path))
        #print("_log_path:{}".format(_log_path))


try:
    CONFIG = Config(ROOT_ELEMENT)
    #print(CONFIG.rootElement)
    #print(CONFIG.connectionString)
except Exception as ex:
    print('Handled Error in Config():{}'.format(str(ex)))
    raise ex



