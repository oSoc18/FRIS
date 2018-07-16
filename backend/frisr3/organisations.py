import zeep
from frisr3.fris_utils import localize_text

SCHEME = 'https://frisr3.researchportal.be/ws/OrganisationServiceFRIS?wsdl'
SETTINGS = zeep.Settings(strict=False)

class Organisation:
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.uuid
    
    @property
    def name(self):
        return self.localized_name()

    def localized_name(self, locale='en'):
        return localize_text(self.data.name, locale)

    @property
    def acronym(self):
        return self.data.acronym
    
    @property
    def keywords(self):
        return self.localized_keywords()

    def localized_keywords(self, locale='en'):
        keywords = self.data.keywords.keyword
        return [k._value_1 for k in keywords if k.locale == locale]

    @property
    def research_activity(self):
        return self.localized_research_activity()

    def localized_research_activity(self, locale='en'):
        return localize_text(self.data.researchActivity, locale) 


class OrganisationService:
    def __init__(self):
        self.client = zeep.Client(wsdl=SCHEME, settings=SETTINGS)

    def find_organisation(self, uuid: str) -> Organisation:
        response = self.client.service.getOrganisations({
            'uuids': [{ 'identifier': uuid }],
        })
        if len(response.organisation) > 0:
            data = response.organisation[0]
            return Organisation(data)