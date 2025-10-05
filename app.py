from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
import os
import requests
from dotenv import load_dotenv
import pickle
import numpy as np

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "hackriculturesecret")

# Try loading your ML models if present
yield_model = None
irri_model = None
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
try:
    with open(os.path.join(MODEL_DIR, "yield_model.pkl"), "rb") as f:
        yield_model = pickle.load(f)
except Exception as e:
    print("Yield model not loaded:", e)
try:
    with open(os.path.join(MODEL_DIR, "irri_model.pkl"), "rb") as f:
        irri_model = pickle.load(f)
except Exception as e:
    print("Irrigation model not loaded:", e)

# Helper to fetch weather for a city name (OpenWeatherMap)
def fetch_weather_for_location(location):
    if not WEATHER_API_KEY:
        return {"error": "No weather API key configured."}
    # Use OWM current weather endpoint
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        if resp.status_code != 200:
            return {"error": data.get("message", "Error fetching weather.")}
        main = data.get("main", {})
        wind = data.get("wind", {})
        return {
            "temperature": main.get("temp"),
            "humidity": main.get("humidity"),
            "wind_speed": wind.get("speed")
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/about")
def about():
    # sample developers info
    developers = [
        {"name":"Dev One","img":url_for('static', filename='images/dev1.jpg'), "linkedin":"https://linkedin.com/in/dev1","github":"https://github.com/dev1","role":"Frontend"},
        {"name":"Dev Two","img":url_for('static', filename='images/dev2.jpg'), "linkedin":"https://linkedin.com/in/dev2","github":"https://github.com/dev2","role":"Backend"},
        {"name":"Dev Three","img":url_for('static', filename='images/dev3.jpg'), "linkedin":"https://linkedin.com/in/dev3","github":"https://github.com/dev3","role":"ML"},
        {"name":"Dev Four","img":url_for('static', filename='images/dev4.jpg'), "linkedin":"https://linkedin.com/in/dev4","github":"https://github.com/dev4","role":"Data"}
    ]
    return render_template("about.html", developers=developers)

@app.route("/get_weather", methods=["POST"])
def get_weather():
    data = request.json or {}
    location = data.get("location", "")
    if not location:
        return jsonify({"error":"No location provided."}), 400
    res = fetch_weather_for_location(location)
    if "error" in res:
        return jsonify({"error": res["error"]}), 400
    return jsonify(res)

# Yield prediction page (form + POST)
@app.route("/yield_predict", methods=["GET","POST"])
def yield_predict():
    crops = ["Barley","Corn","Cotton","Potato","Rice","Soybean","Sugarcane","Sunflower","Tomato","Wheat"]
    soils = ["Clay","Loamy","Peaty","Saline","Sandy"]
    if request.method == "POST":
        form = request.form
        # gather float inputs
        try:
            Soil_pH = float(form.get("Soil_pH","0") or 0)
            Temperature = float(form.get("Temperature","0") or 0)
            Humidity = float(form.get("Humidity","0") or 0)
            Wind_Speed = float(form.get("Wind_Speed","0") or 0)
            N = float(form.get("N","0") or 0)
            P = float(form.get("P","0") or 0)
            K = float(form.get("K","0") or 0)
            Soil_Quality = float(form.get("Soil_Quality","0") or 0)
        except ValueError:
            flash("Please enter valid numeric values.", "danger")
            return redirect(url_for('yield_predict'))

        crop = form.get("Crop_Type")
        soil = form.get("Soil_Type")
        # Create feature vector according to the exact order your model expects.
        # Here we provide a simple example mapping; adjust this to match your training.
        # Example feature order:
        # [Soil_pH, Temperature, Humidity, Wind_Speed, N, P, K, Soil_Quality,
        #  Crop_Barley, Crop_Corn, ..., Soil_Clay, Soil_Loamy,...]
        crop_onehot = [1 if crop==c else 0 for c in crops]
        soil_onehot = [1 if soil==s else 0 for s in soils]
        features = [Soil_pH, Temperature, Humidity, Wind_Speed, N, P, K, Soil_Quality] + crop_onehot + soil_onehot
        X = np.array(features).reshape(1, -1)

        if yield_model:
            try:
                pred = yield_model.predict(X)[0]
                pred_val = float(pred)
            except Exception as e:
                pred_val = None
                flash("Model error: "+str(e), "warning")
        else:
            # Dummy prediction logic: simple formula for demonstration
            pred_val = round((N + P + K) * 0.1 + (7 - abs(7 - Soil_pH)) * 0.5 + Soil_Quality * 0.2, 2)

        return render_template("yield_form.html", crops=crops, soils=soils, prediction=pred_val, inputs=form)

    return render_template("yield_form.html", crops=crops, soils=soils, prediction=None, inputs=None)

# Irrigation recommendation
@app.route("/irrigation", methods=["GET","POST"])
def irrigation():
    crops = ["Rice"]  # per requirement (only rice)
    if request.method == "POST":
        crop = request.form.get("crop_name")
        try:
            moisture = float(request.form.get("moisture","0") or 0)
            temp = float(request.form.get("temp","0") or 0)
        except ValueError:
            flash("Enter valid numeric values.", "danger")
            return redirect(url_for('irrigation'))

        # If you have a model: use irri_model; else simple rule-of-thumb
        if irri_model:
            try:
                X = np.array([moisture, temp]).reshape(1,-1)
                out = irri_model.predict(X)[0]
                needed = bool(out)
            except Exception as e:
                needed = moisture < 40  # fallback rule
                flash("Irrigation model error: "+str(e), "warning")
        else:
            # Basic threshold rule: below 40% moisture -> need irrigation
            needed = moisture < 40

        result_text = ""
        if needed:
            result_text = f"Yes irrigation needed for {crop} at {temp}°C"
        else:
            result_text = f"No irrigation needed for {crop} at {temp}°C"

        return render_template("irrigation.html", crops=crops, result=result_text, inputs=request.form)

    return render_template("irrigation.html", crops=crops, result=None, inputs=None)

if __name__ == "__main__":
    app.run(debug=True)
