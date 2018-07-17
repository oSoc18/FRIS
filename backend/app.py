from flask import Flask, request, jsonify, abort
from flask_cors import CORS,cross_origin
from frisr3.organisations import OrganisationService

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return "Hello oSoC!"


@app.route('/organisation/<uuid>')
@cross_origin()
def organisation(uuid=None):
    service = OrganisationService()
    org = service.find_organisation(uuid)
    if not org:
        abort(404)
    return jsonify(org.attributes)


@app.route('/organisations')
@cross_origin()
def list_organisations():
    keyword = request.args.get('keyword')
    service = OrganisationService()
    #  TODO: do this properly ..
    if keyword:
        results = service.find_by_keyword(keyword)
        return jsonify([org.attributes() for org in results])
    return 'ok'

# TODO: how do we want to handle this case?
# I think we want multiple json representations for the same object ...

if __name__ == '__main__':
    app.run(debug=True)
