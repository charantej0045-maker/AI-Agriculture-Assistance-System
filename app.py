from flask import Flask, render_template, request, jsonify, Response
import csv
import io

app = Flask(__name__)


def calculate_recommendation(data):
    soil = data.get("soil", "Loamy")
    season = data.get("season", "Kharif")
    temp = float(data.get("temp", 27))
    humidity = float(data.get("humidity", 68))
    rain = float(data.get("rain", 720))
    moisture = float(data.get("moisture", 42))
    n = float(data.get("n", 82))
    p = float(data.get("p", 48))
    k = float(data.get("k", 46))

    crop = "Rice"
    if season == "Rabi":
        crop = "Wheat"
    if season == "Summer":
        crop = "Maize"
    if soil == "Black Soil" and season == "Rabi":
        crop = "Cotton"
    if soil == "Sandy" and rain < 500:
        crop = "Groundnut"

    fertilizer = "Balanced NPK"
    if n < 50:
        fertilizer = "Nitrogen-rich fertilizer"
    elif p < 30:
        fertilizer = "Phosphorus-rich fertilizer"
    elif k < 30:
        fertilizer = "Potassium-rich fertilizer"

    score = 50
    if 20 <= temp <= 32:
        score += 15
    if 45 <= humidity <= 80:
        score += 10
    if 30 <= moisture <= 65:
        score += 15
    if 400 <= rain <= 1200:
        score += 10
    score = max(0, min(100, score))

    yield_value = round(2.5 + (score / 100) * 3.2, 2)
    water_need = round(max(3, min(8, (6 - rain / 300 + (50 - moisture) / 30))), 1)

    return {
        "crop": crop,
        "fertilizer": fertilizer,
        "yield": f"{yield_value} ton/ha",
        "water": f"{water_need} mm/day",
        "score": int(score),
        "message": (
            "The system analyzed soil, season, temperature, humidity, rainfall, moisture, and NPK values "
            "to recommend the best crop and fertilizer plan for your field."
        )
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend_api():
    try:
        data = request.get_json(force=True)
        result = calculate_recommendation(data)
        return jsonify({"success": True, **result})
    except Exception as exc:  # pragma: no cover
        return jsonify({"success": False, "message": f"Error: {str(exc)}"}), 400


@app.route("/api/report", methods=["POST"])
def export_report():
    try:
        data = request.get_json(force=True)
        result = calculate_recommendation(data)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Field Report", "Value"])
        writer.writerow(["Soil Type", data.get("soil", "")])
        writer.writerow(["Season", data.get("season", "")])
        writer.writerow(["Temperature", data.get("temp", "")])
        writer.writerow(["Humidity", data.get("humidity", "")])
        writer.writerow(["Rainfall", data.get("rain", "")])
        writer.writerow(["Moisture", data.get("moisture", "")])
        writer.writerow(["Nitrogen", data.get("n", "")])
        writer.writerow(["Phosphorus", data.get("p", "")])
        writer.writerow(["Potassium", data.get("k", "")])
        writer.writerow(["Recommended Crop", result["crop"]])
        writer.writerow(["Fertilizer", result["fertilizer"]])
        writer.writerow(["Estimated Yield", result["yield"]])
        writer.writerow(["Water Requirement", result["water"]])
        writer.writerow(["Score", f"{result['score']}%"])

        response = Response(output.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = 'attachment; filename="agriculture_report.csv"'
        return response
    except Exception as exc:  # pragma: no cover
        return jsonify({"success": False, "message": f"Error: {str(exc)}"}), 400


if __name__ == "__main__":
    app.run(debug=True)
