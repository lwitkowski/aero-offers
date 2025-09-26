from flask import Flask, jsonify, request, abort
from flask_headers import headers
from flask_cors import CORS
from classifier import classifier
import offers_db
from offer import AircraftCategory

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/api/models")
@headers({"Cache-Control": "public, max-age=360"})
def aircraft_models():
    return jsonify(classifier.get_all_models())


@app.route("/api/offers")
def offers():
    raw_category = request.args.get("category")
    try:
        category = AircraftCategory[raw_category] if raw_category is not None else None
    except Exception:
        category = AircraftCategory.unknown
    return jsonify(
        offers_db.get_offers(
            category=category,
            offset=int(request.args.get("offset") or "0"),
            limit=int(request.args.get("limit") or "30"),
        )
    )


@app.route("/api/offers/<manufacturer>/<model>")
def model_information(manufacturer, model):
    """
    Returns statistics for a specific manufacturer and model
    """
    manufacturers = classifier.get_all_models()
    if manufacturer not in manufacturers:
        abort(404)

    return jsonify(
        dict(
            manufacturer_website=manufacturers[manufacturer].get(
                "manufacturer_website", None
            ),
            offers=offers_db.get_offers(
                manufacturer=manufacturer, model=model, limit=300
            ),
        )
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8082, debug=False)
