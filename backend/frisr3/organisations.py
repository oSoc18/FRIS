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
        if self.data.keywords is None:
            return None
        keywords = self.data.keywords.keyword
        return [k._value_1 for k in keywords if k.locale == locale]

    def research_activity(self, locale=DEFAULT_LOCALE):
        return localize_text(self.data.researchActivity, locale)
    
    def root_organisation_uuid(self):
        return self.data.rootOrganisationUuid
    
    def is_root_organisation(self):
        return self.uuid() == self.root_organisation_uuid()
    
    def __repr__(self):
        return self.name()

    def __hash__(self):
        return self.uuid().__hash__()
    
    def __eq__(self, other):
        return self.uuid() == other.uuid()

    def attributes(self):
        return {
            'uuid': self.uuid(),
            'name': self.name(),
            'acronym': self.acronym(),
            'keywords': self.keywords(),
            'research_activity': self.research_activity(),
        }

class OrganisationService:
    def __init__(self):
        self.client = zeep.Client(wsdl=WSDL_URL, settings=CLIENT_SETTINGS)

    def find_organisations(self, uuids):
        uuids = list(uuids)
        response = self.client.service.getOrganisations({
            'uuids': [{ 'identifier': uuids }],
            'window': {
                'pageSize': len(uuids),
                'pageNumber': zeep.xsd.SkipValue,
                'orderings': zeep.xsd.SkipValue,
            }
        })
        orgs = [Organisation(o) for o in response.organisation]
        return orgs

    def find_organisation(self, uuid: str) -> Organisation:
        return self.find_organisations([uuid])[0]

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