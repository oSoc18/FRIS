import zeep
from frisr3.settings import *
from frisr3.fris_utils import localize_text

WSDL_URL = 'https://frisr3.researchportal.be/ws/ResearchOutputServiceFRIS?wsdl'
CLIENT_SETTINGS = zeep.Settings(strict=False)

class ResearchOutput:
    def __init__(self, data):
        self.data = data

    def uuid(self):
        return self.data.uuid

    def title(self, locale=DEFAULT_LOCALE):
        return localize_text(self.data.title, locale)
    
    def abstract(self, locale=DEFAULT_LOCALE):
        return localize_text(self.data.abstract, locale)

    def keywords(self, locale=DEFAULT_LOCALE):
        keywords = self.data.keywords
        return [k._value_1 for k in keywords if k.locale == locale]

class ResearchOutputService:
    def __init__(self):
        self.client = zeep.Client(wsdl=WSDL_URL, settings=CLIENT_SETTINGS)

    def get_outputs(self, params={}):
        request_params = {}

        page_size = params.get('page_size', DEFAULT_PAGE_SIZE)

        request_params['window'] = {
            'pageSize': page_size,
            'pageNumber': 0,
            'orderings': zeep.xsd.SkipValue
        }


        page_number = 0
        while True:
            request_params['window']['pageNumber'] = page_number
            response = self.client.service.getResearchOutput(request_params)

            for obj in response._value_1:
                for output in obj.values():
                    yield ResearchOutput(output)

            page_number += 1
            if response.total <= page_size * page_number:
                return