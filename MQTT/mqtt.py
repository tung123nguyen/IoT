import paho.mqtt.client as mqtt

# Khi nhận được message
def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)

client.subscribe("home/livingroom/temperature")
client.on_message = on_message

# Gửi dữ liệu
client.publish("home/livingroom/temperature", "25.3")

client.loop_forever()