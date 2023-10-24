from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import json

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


@app.post('/predict')
def predict_crop(data: model_input):

    input_data = data.json()
    input_dict = json.loads(input_data)

    N = input_dict['N']
    P = input_dict['P']
    K = input_dict['K']
    temperature = input_dict['temperature']
    humidity = input_dict['humidity']
    ph = input_dict['ph']
    rainfall = input_dict['rainfall']

    input_list = [N, P, K, temperature, humidity, ph, rainfall]

    predict_crop = model.predict([input_list])
    prediction = predict_crop.tolist()
    return {'prediction': prediction[0]}
