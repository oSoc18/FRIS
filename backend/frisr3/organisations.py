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
    
    def localized_name(self, locale='en'):
        name = self.data.name
        if name:
            return localize_text(name, locale=locale)
        else:
            return None


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
