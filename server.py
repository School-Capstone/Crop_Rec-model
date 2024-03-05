from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import pickle
from fastapi.responses import HTMLResponse

app = FastAPI()

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
model = pickle.load(open('./model/CropRecom_LogisticRegresion.pkl', 'rb'))

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
    </style>
    <script>
        var socket = new WebSocket("ws://localhost:8000/ws");

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
            var N = document.getElementById("NInput").value;
            var P = document.getElementById("PInput").value;
            var K = document.getElementById("KInput").value;
            var temperature = document.getElementById("temperatureInput").value;
            var humidity = document.getElementById("humidityInput").value;
            var ph = document.getElementById("phInput").value;
            var rainfall = document.getElementById("rainfallInput").value;

            var message = JSON.stringify({
                "N": N,
                "P": P,
                "K": K,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            });

            socket.send(message);
        }
    </script>
</head>
<body>
    <h1>WebSocket Client</h1>
    <p>Enter the input values to get the prediction</p>
    <div id="results"></div>
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        try:
            input_data = model_input.parse_raw(data)
            input_list = [input_data.N, input_data.P, input_data.K, input_data.temperature,
                          input_data.humidity, input_data.ph, input_data.rainfall]
            predict_crop = model.predict([input_list])
            prediction = predict_crop.tolist()
            await websocket.send_text(f"Prediction: {prediction[0]}")
        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
