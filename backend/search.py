from frisr3.research_outputs import ResearchOutputService

def search_keyword(search_term: str, num_outputs=100):
    service = ResearchOutputService()

    # find outputs
    outputs = service.outputs(
        keyword=search_term,
        count=num_outputs,
    )

    # group outputs by organisation
    data = {}
    for output in outputs:
        for org in output.associated_organisations():
            if not org.uuid() in data:
                data[org.uuid()] = {
                    'organisation': org.attributes(),
                    'researchOutputs': [],
                }
            data[org.uuid()]['researchOutputs'].append(output.attributes())

    return list(data.values())