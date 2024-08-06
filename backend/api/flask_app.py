from flask import Flask, jsonify, request, abort
from flask_headers import headers
from flask_cors import CORS
from classifier import classifier
import db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/models")
@headers({'Cache-Control':'public, max-age=360'})
def aircraft_models():
    return jsonify(classifier.get_all_models())

@app.route('/api/offers')
def offers():
    return jsonify(db.get_offers(aircraft_type=request.args.get('aircraft_type'),
                                      offset=int(request.args.get('offset') or '0'),
                                      limit=int(request.args.get('limit') or '30')))

@app.route("/api/offers/<manufacturer>/<model>")
def model_information(manufacturer, model):
    """
    Returns statistics for a specific manufacturer and model
    """
    manufacturers = classifier.get_all_models()
    if manufacturer not in manufacturers:
        abort(404)
    manufacturer_info = manufacturers[manufacturer]
    del (manufacturer_info["models"])  # remove models info
    manufacturer_info["offers"] = db.get_offers(manufacturer=manufacturer, model=model)
    return jsonify(manufacturer_info)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
