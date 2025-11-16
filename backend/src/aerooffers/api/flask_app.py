from flask import abort, Flask, jsonify, request, Response
from flask_cors import CORS
from flask_headers import headers

from aerooffers.classifier import classifier
from aerooffers.offer import AircraftCategory
from aerooffers.offers_db import get_offers

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/api/models")
@headers({"Cache-Control": "public, max-age=360"})
def aircraft_models() -> Response:
    return jsonify(classifier.get_all_models())


@app.route("/api/offers")
def offers() -> Response:
    raw_category = request.args.get("category")
    try:
        category = AircraftCategory[raw_category] if raw_category is not None else None
    except Exception:
        category = AircraftCategory.unknown
    return jsonify(
        get_offers(
            category=category,
            offset=int(request.args.get("offset") or "0"),
            limit=int(request.args.get("limit") or "30"),
        )
    )


@app.route("/api/offers/<manufacturer>/<model>")
def model_information(manufacturer: str, model: str) -> Response:
    """Returns statistics for a specific manufacturer and model"""
    manufacturers = classifier.get_all_models()
    if manufacturer not in manufacturers:
        abort(404)

    return jsonify(
        dict(
            manufacturer_website=manufacturers[manufacturer].get(
                "manufacturer_website", None
            ),
            offers=get_offers(manufacturer=manufacturer, model=model, limit=300),
        )
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8082, debug=False)
