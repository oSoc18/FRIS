from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from frisr3.organisations import OrganisationService
from frisr3.research_outputs import ResearchOutputService
from cluster import cluster_outputs

from flask_caching import Cache

import socket
app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 60*60*24,
})
CORS(app)


@app.route('/')
def index():
    return "Hello oSoC!"


@app.route('/organisation/<uuid>')
@cache.cached()
def organisation(uuid=None):
    service = OrganisationService()
    org = service.find_organisation(uuid)
    if not org:
        abort(404)

    if org.is_root_organisation():
        root_org = None
    else:
        r_org = service.find_organisation(org.root_organisation_uuid())
        root_org = r_org.attributes()

    return jsonify({
        **org.attributes(),
        'root_organisation': root_org,
    })


# how many research outputs to consider for the search
NUM_OUTPUTS = 100
@app.route('/organisations/search')
def organisation_search():
    keyword = request.args.get('keyword', '')
    data = find_organisations(keyword)
    return jsonify(data)

@cache.memoize()
def find_organisations(keyword):
    # find outputs
    outputs = ResearchOutputService().outputs(
        keyword=keyword,
        count=NUM_OUTPUTS,
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

    data = []
    for org in orgs:
        if org.root_organisation_uuid() in root_org_map:
            root_org = root_org_map[org.root_organisation_uuid()].attributes()
        else:
            root_org = None
        data.append({
            'organisation': {
                **org.attributes(),
                'root_organisation': root_org,
            },
            'researchOutputs': org_outputs[org.uuid()],
        })
    
    data.sort(key=lambda d: len(d['researchOutputs']), reverse=True)
    return data




@app.route('/organisation/<uuid>/output_cluster')
@cache.memoize()
def organisation_output_cluster(uuid):
    organisation_service = OrganisationService()
    org = organisation_service.find_organisation(uuid)
    if not org:
        abort(404)
    output_service = ResearchOutputService()
    outputs = list(output_service.outputs(organisation=uuid))
    tree = cluster_outputs(outputs)
    tree['name'] = org.name()
    return jsonify(tree)


if __name__ == '__main__':
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    if(IP == '127.0.1.1'):
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        app.run(host='openexpertise.be', port=5000, debug=True, ssl_context=('/etc/letsencrypt/live/openexpertise.be/cert.pem', '/etc/letsencrypt/live/openexpertise.be/privkey.pem'))
    else:
        app.run(debug=True)
