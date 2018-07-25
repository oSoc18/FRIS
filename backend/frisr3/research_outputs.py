import zeep
from frisr3.settings import *
from frisr3.fris_utils import localize_text
from frisr3.organisations import Organisation

from typing import Iterator

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
        return localize_text(self.data.researchAbstract, locale)
    
    def publication_date(self):
        return self.data.publicationDate

    def keywords(self, locale=DEFAULT_LOCALE):
        if not self.data.keywords:
            return []
        keywords = self.data.keywords.keyword
        return [k._value_1 for k in keywords if k.locale == locale]
    
    # TODO: this is ugly.
    def associated_organisations(self):
        organisation_ids = set()
        participants = self.data.participants.participant
        assignments = [p.assignment for p in participants if p.assignment]
        for assignment in assignments:
            organisation_ids.add(assignment.organisation.uuid)
        return organisation_ids
    
    def attributes(self):
        return {
            'uuid': self.uuid(),
            'title': self.title(),
            'abstract': self.abstract(),
            'keywords': self.keywords(),
            'publication_date': self.publication_date(),
        }


class ResearchOutputQuery:
    def __init__(self, client: zeep.Client, params: dict):
        self.client = client
        self.params = params
    
    def query_params(self):
        locale = self.params.get('locale', DEFAULT_LOCALE)
        p = {}

        if 'keyword' in self.params:
            keyword = self.params['keyword']
            p['keyword'] = [{
                'search': keyword,
                'locale': locale,
            }]
        
        if 'organisation' in self.params:
            org = self.params['organisation']
            p['associatedOrganisations'] = [{ 'identifier': org}]
        
        return p
    
    def results(self) -> Iterator[ResearchOutput]:
        request_params = self.query_params()

        # determine page size
        page_size = self.params.get('page_size', DEFAULT_PAGE_SIZE)

        count = self.params.get('count')
        if count:
            page_size = min(page_size, count)

        request_params['window'] = {
            'pageSize': page_size,
            'orderings': zeep.xsd.SkipValue,
        }

        page_number = 0
        while True:
            request_params['window']['pageNumber'] = page_number
            response = self.client.service.getResearchOutput(request_params)

            # TODO: should this be done here?
            if count is None:
                count = response.total

            for elem in response._value_1:
                for output in elem.values():
                    yield ResearchOutput(output)
            
            page_number += 1
            if page_number * page_size >= count:
                # all results fetched!
                break
    
    def __iter__(self) -> Iterator[ResearchOutput]:
        return self.results()


class ResearchOutputService:
    def __init__(self):
        self.client = zeep.Client(wsdl=WSDL_URL, settings=CLIENT_SETTINGS)

    def outputs(self, **kwargs) -> ResearchOutputQuery:
        return ResearchOutputQuery(self.client, kwargs)
