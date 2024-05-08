from fastapi import FastAPI, WebSocket, Depends
from pydantic import BaseModel
import pickle
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import DBSessionMiddleware, db
from schema import Predictions as SchemaPredictions
from models import Predictions as ModelPredictions
import os
from datetime import datetime
import json
import ast



from models import Users  # Assuming you have a Users model defined in models.py
# Assuming you have a function to create a database session in database.py
import bcrypt  # For hashing passwords
import re

app = FastAPI()


uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.add_middleware(DBSessionMiddleware, db_url=uri)


# NPK ,temperature ,humidity , ph ,rainfall


class model_input(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


# loading the model
# model = pickle.load(open('./model/CropRecom_LogisticRegresion.pkl', 'rb'))


model_paths = {
    "CropRecom_LogisticRegresion": "./model/CropRecom_LogisticRegresion.pkl",
    "CropRecom_Classification": "./model/CropRecom_Classification.pkl"
}

html = """
<html>
<head>
    <title>WebSocket Client</title>
        <style>
        body {
            background-color: #f2f2f2;
            font-family: Arial, sans-serif;
        }

        h1 {
            color: #333333;
            text-align: center;
        }

        input[type="number"], button {
            padding: 10px;
            margin: 5px;
            border: none;
            border-radius: 5px;
        }

        input[type="number"] {
            width: 200px;
        }

        button {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }

        button:hover {
            background-color: #45a049;
        }

        #results {
            margin-top: 20px;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 5px;
            align-text: center;
        }
        select {
            padding: 10px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            width: 200px;
        }
    </style>
    <script>
        var socket = new WebSocket("wss://croprecstaging-201b04c79344.herokuapp.com/ws");

        socket.onopen = function(event) {
            console.log("WebSocket connection established.");
        };

        socket.onmessage = function(event) {
            var resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = event.data;
            console.log("Received message:", event.data);
        };

        socket.onclose = function(event) {
            console.log("WebSocket connection closed.");
        };

function sendMessage() {
        var N = parseFloat(document.getElementById("NInput").value);
        var P = parseFloat(document.getElementById("PInput").value);
        var K = parseFloat(document.getElementById("KInput").value);
        var temperature = parseFloat(document.getElementById("temperatureInput").value);
        var humidity = parseFloat(document.getElementById("humidityInput").value);
        var ph = parseFloat(document.getElementById("phInput").value);
        var rainfall = parseFloat(document.getElementById("rainfallInput").value);
        var modelType = document.getElementById("modelTypeInput").value;

        var message = JSON.stringify({
            "data": {
                "N": N,
                "P": P,
                "K": K,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            },
            "model_type": modelType
        });

        socket.send(message);
    }
    </script>
</head>
<body>
    <h1>WebSocket Client</h1>
    <p>Enter the input values to get the prediction</p>
    <div id="results"></div>
    <select id="modelTypeInput">
    <option value="CropRecom_LogisticRegresion">Crop Recommendation (Logistic Regression)</option>
    <option value="CropRecom_Classification">Crop Recommendation (Classification)</option>
    </select>
    <input type="number" id="NInput" placeholder="Enter N">
    <input type="number" id="PInput" placeholder="Enter P">
    <input type="number" id="KInput" placeholder="Enter K">
    <input type="number" id="temperatureInput" placeholder="Enter temperature">
    <input type="number" id="humidityInput" placeholder="Enter humidity">
    <input type="number" id="phInput" placeholder="Enter ph">
    <input type="number" id="rainfallInput" placeholder="Enter rainfall">
    <button onclick="sendMessage()">Send</button>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)




# Set default model type
DEFAULT_MODEL_TYPE = "CropRecom_Classification"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                input_data = model_input.parse_obj(message.get("data", {}))
                model_type = message.get("model_type", DEFAULT_MODEL_TYPE)

                # Load the selected model
                if model_type in model_paths:
                    with open(model_paths[model_type], 'rb') as model_file:
                        model = pickle.load(model_file)
                else:
                    raise ValueError("Invalid model type")

                input_list = [input_data.N, input_data.P, input_data.K, input_data.temperature,
                              input_data.humidity, input_data.ph, input_data.rainfall]
                predict_crop = model.predict([input_list])
                prediction = predict_crop.tolist()[0]

                # Save prediction to the database
                with db():
                    new_prediction = ModelPredictions(
                        date=str(datetime.now()),
                        prediction=prediction,
                        actual=None,
                        error=None,
                        model=model_type,
                        model_type=model_type,
                        data=str(input_data.dict()),
                        data_source="webapp"
                    )
                    db.session.add(new_prediction) 
                    db.session.commit()

                await websocket.send_text(prediction)
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    except WebSocketDisconnect:
        # Handle WebSocket disconnection
        print("Client disconnected")
        # Perform any necessary cleanup or handle the disconnection as needed
        await websocket.close()
        


        

@app.get("/predictions")
async def get_predictions():
    # Create a session context
    with db():
        # Query all predictions from the database
        predictions = db.session.query(ModelPredictions).all()
        if not predictions:
            return {"message": "No predictions found"}
        # Serialize predictions into a dictionary
        serialized_predictions = []
        for prediction in predictions:
            serialized_predictions.append({
                "id": prediction.id,
                "date": prediction.date,
                "prediction": prediction.prediction,
                "actual": prediction.actual,
                "error": prediction.error,
                "model": prediction.model,
                "model_type": prediction.model_type,
                "data": prediction.data,
                "data_source": prediction.data_source
            })
        return serialized_predictions

@app.get("/predictions/{prediction_id}")
async def get_prediction_by_id(prediction_id: str):
    # Create a session context
    with db():
        # Query the prediction by ID from the database
        prediction = db.session.query(ModelPredictions).filter_by(id=prediction_id).first()
        if prediction:
            # Serialize the prediction into a dictionary
            serialized_prediction = {
                "id": prediction.id,
                "date": prediction.date,
                "prediction": prediction.prediction,
                "actual": prediction.actual,
                "error": prediction.error,
                "model": prediction.model,
                "model_type": prediction.model_type,
                "data": ast.literal_eval(prediction.data),
                "data_source": prediction.data_source
            }
            return serialized_prediction
        else:
            return {"message": "Prediction not found"}
