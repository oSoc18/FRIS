import zeep

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

    @property
    def acronym(self):
        return self.data.acronym
    
    @property
    def keywords(self):
        return self.localized_keywords()
    
    @property
    def research_activity(self):
        return self.localized_research_activity()
    
    def localized_name(self, locale='en'):
        text = self.data.name
        if not text:
            return None
        return localize_text(text, locale)

    def localized_keywords(self, locale='en'):
        keywords = self.data.keywords.keyword
        return [k._value_1 for k in keywords if k.locale == locale]
    
    def localized_research_activity(self, locale='en'):
        text = self.data.researchActivity
        if not text:
            return None
        return localize_text(text, locale) 



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


def localize_text(localized_text, locale='en'):
    """ Get a value from a FRIS LocalizedText object """
    for text in localized_text.texts.text:
        if text.locale == locale:
            return text._value_1
    return None
