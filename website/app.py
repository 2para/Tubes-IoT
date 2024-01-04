import paho.mqtt.client as mqtt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import numpy as np
from flask import Flask, request, render_template, jsonify, current_app
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from tensorflow import keras
import numpy as np
from keras.models import load_model
from joblib import load
import logging
import threading
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Load the trained model
loaded_model = keras.models.load_model("neural_network.h5")  # Replace with your model file

# Dictionary to convert class indices to labels
label_to_idx_inv = {0: "Not suitable", 1: "Suitable"}

import paho.mqtt.client as mqtt

# MQTT broker connection details
mqtt_broker = "broker.mqtt-dashboard.com"
mqtt_port = 1883
mqtt_topic = "tempt"
 
def classify(temperature, humidity):
    light = random.uniform(0.0, 900.0)
    co2 = random.uniform(0.0, 1200.0)
    humidRatio = random.uniform(0.0, 0.006)
    # Perform prediction
    predicted_class = loaded_model.predict(np.array([temperature, humidity, light, co2, humidRatio]).reshape(1, -1))  # Assuming other sensor data as zeros

    # Get the class with the highest probability as the prediction
    #predicted_label = label_to_idx_inv[np.argmax(predicted_class)]

    if predicted_class == 1:
        status = "Suitable"
    else:
        status = "Not Suitable"
    return status


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global temperature, humidity
    data = msg.payload.decode()
    extracted = data.split(",")
    temperature = float(extracted[0].split(": ")[1].split("}")[0])  # Extract temperature as an integer
    humidity = float(extracted[1].split(": ")[1].split("}")[0])        # Extract humidity as an integer
    result = classify(temperature, humidity)
    display(result)

def display(result):
    socketio.emit("tempthumid", {"Status":result})

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the loop to process incoming messages
client.loop_start()

@app.route('/')
def home():
    return render_template('habitable.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.json
        temperature = float(data.get("Temperature"))
        humidity = float(data.get("Humidity"))
        result = classify(temperature, humidity)
        display(result)
        return jsonify({"Temperature":temperature, "Humidity":humidity, "Status":result})


if __name__ == '__main__':
    app.run(debug=True)

socketio.run(app)