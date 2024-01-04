#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "mirai";
const char* password = "iwnqish191u";
const char* mqtt_server = "broker.mqtt-dashboard.com"; // Replace with your MQTT broker IP

const int mqtt_port = 1883;                            // MQTT broker port
const char* mqtt_topic = "tempt";       // MQTT topic to publish data

WiFiClient espClient;
PubSubClient client(espClient);

#define DHTPIN 2       // Pin where the DHT11 is connected
#define DHTTYPE DHT11  // Type of the DHT sensor

DHT dht(DHTPIN, DHTTYPE);
#define MSG_BUFFER_SIZE 50
char msg[MSG_BUFFER_SIZE];

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT broker...");
    if (client.connect("ESP32Client")) {
      Serial.println("Connected to MQTT broker");
      client.subscribe(mqtt_topic); // Subscribe to the topic after reconnection
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");

  client.setServer(mqtt_server, mqtt_port);

  dht.begin();
}

void loop() {
  delay(100);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  snprintf(msg, MSG_BUFFER_SIZE, "{\"temperature\": %.2f, \"humidity\": %.2f}", temperature, humidity);

  if (client.publish(mqtt_topic, msg)) {
    Serial.println("Data sent to MQTT broker:");
    Serial.println(msg);
  } else {
    Serial.println("Failed to send data to MQTT broker");
    client.disconnect(); // Disconnect from the broker to attempt reconnection
    reconnect();
  }

  client.loop();
}
