import datetime

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from classifier import classifier

import db
from my_logging import *

app = Flask(__name__)
# TODO verify security risks with this
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['JSON_AS_ASCII'] = False

logger = logging.getLogger("api")


@app.route('/offers')
def offers():
    logger.debug("Received request {0}".format(request))
    return jsonify(db.get_offers_dict(limit=request.args.get('limit'),
                                      order_by=request.args.get('orderBy'),
                                      offset=request.args.get('offset'),
                                      aircraft_type=request.args.get('aircraft_type')))

@app.route("/model/<manufacturer>/<model>")
def model_information(manufacturer, model):
    """
    Returns statistics for a specific manufacturer and model
    """
    manufacturers = classifier.get_all_models()
    if manufacturer not in manufacturers:
        abort(404)
    manufacturer_info = manufacturers[manufacturer]
    del (manufacturer_info["models"])  # remove models info
    manufacturer_info["offers"] = db.get_offers_for_model(manufacturer, model)
    return jsonify(manufacturer_info)


@app.route("/models")
def aircraft_models():
    """
    Returns list of matching models in the format:
    [{
        "manufacturer": "Alexander Schleicher",
        "model": "K8b"
    }]
    :param search_str: manufacturer/model to look for
    :return: list of matching models
    """
    search_str = request.args.get('search')
    logger.info("Search request: {0}".format(search_str))
    all_models = classifier.get_all_models()
    matching_models = []
    for manufacturer in all_models:
        for aircraft_type in all_models[manufacturer]["models"]:
            for model in all_models[manufacturer]["models"][aircraft_type]:
                if search_str in manufacturer + " " + model:
                    matching_models.append({
                        "manufacturer": manufacturer,
                        "model": model})
    return jsonify(matching_models)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
