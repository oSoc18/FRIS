from flask import Flask, jsonify, abort
from frisr3.organisations import OrganisationService

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello oSoC!"

@app.route('/organisations/<uuid>')
def organisation(uuid=None):
    service = OrganisationService()
    org = service.find_organisation(uuid)
    if not org:
        abort(404)
    return jsonify({
        'uuid': org.uuid,
        'name': org.name,
        'acronym': org.acronym,
        'keywords': org.keywords,
        'researchActivity': org.research_activity
    })

if __name__ == '__main__':
    app.run(debug=True)