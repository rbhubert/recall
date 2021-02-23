import abc

from enums import sources_base
from enums.type_data import DataType


class InformationPortal(metaclass=abc.ABCMeta):
    datatype = DataType.GENERAL

    @abc.abstractmethod
    def search_with_keywords(self, keywords, model_name):
        pass

    @abc.abstractmethod
    def retrieve_from_urls(self, model_name, url_list):
        pass

    @abc.abstractmethod
    def get_text(self, document):
        pass

    def get_basic_information(self, document):
        return {
            sources_base.URL: document[sources_base.URL],
            sources_base.TITLE: document[sources_base.TITLE],
            sources_base.TEXT: document[sources_base.TEXT],
            sources_base.DATATYPE: self.datatype
        }
