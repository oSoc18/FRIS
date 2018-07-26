from frisr3.research_outputs import ResearchOutputService
from frisr3.organisations import OrganisationService

def search_keyword(search_term: str, num_outputs=100):
    # find outputs
    outputs = ResearchOutputService().outputs(
        keyword=search_term,
        count=num_outputs,
    )

    org_outputs = {}
    for output in outputs:
        for org in output.associated_organisations():
            org_outputs.setdefault(org, []).append(output.attributes())
    
    orgs = OrganisationService().find_organisations(org_outputs.keys())
    root_orgs = OrganisationService().find_organisations({
        org.root_organisation_uuid()
            for org in orgs
            if not org.is_root_organisation() 
    })
    root_org_map = { o.uuid(): o for o in root_orgs }

    data = [{
        'organisation': {
            **org.attributes(),
            'root_organisation': root_org_map.get(org.root_organisation_uuid())
        },
        'researchOutputs': org_outputs[org.uuid()],
    } for org in orgs]
    
    data.sort(key=lambda d: len(d['researchOutputs']), reverse=True)
    return data