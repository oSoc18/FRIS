import zeep
from frisr3.settings import DEFAULT_LOCALE
from frisr3.fris_utils import localize_text

WSDL_URL = 'https://frisr3.researchportal.be/ws/OrganisationServiceFRIS?wsdl'
CLIENT_SETTINGS = zeep.Settings(strict=False)

class Organisation:
    def __init__(self, data):
        self.data = data

    def uuid(self):
        return self.data.uuid
    
    def name(self, locale=DEFAULT_LOCALE):
        return localize_text(self.data.name, locale)

    def acronym(self):
        return self.data.acronym
    
    def keywords(self, locale=DEFAULT_LOCALE):
        keywords = self.data.keywords.keyword
        return [k._value_1 for k in keywords if k.locale == locale]

    def research_activity(self, locale=DEFAULT_LOCALE):
        return localize_text(self.data.researchActivity, locale) 


class OrganisationService:
    def __init__(self):
        self.client = zeep.Client(wsdl=WSDL_URL, settings=CLIENT_SETTINGS)

    def find_organisation(self, uuid: str) -> Organisation:
        response = self.client.service.getOrganisations({
            'uuids': [{ 'identifier': uuid }],
        })
        if len(response.organisation) > 0:
            data = response.organisation[0]
            return Organisation(data)

    def find_by_keyword(self, keyword):
        response = self.client.service.getOrganisations({
            'keyword': [{ 'search': keyword }],
            'window': {
                'pageSize': 100,
                'pageNumber': 0,
                'orderings': zeep.xsd.SkipValue
            }
        })
        return [Organisation(org) for org in response.organisation]