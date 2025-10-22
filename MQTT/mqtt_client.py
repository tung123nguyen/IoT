import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import random

# ======= Cấu hình =======
BROKER = "test.mosquitto.org"  # bạn có thể thay bằng broker bạn muốn
PORT = 1883
CLIENT_ID = "Tung20225426"        # ID của client — dùng để nhận định thiết bị
TOPIC_STATUS = f"iot/{CLIENT_ID}/status"
TOPIC_SENSOR = f"iot/{CLIENT_ID}/sensor"

# ======= Callback =======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Kết nối thành công đến broker.")
        # Gửi trạng thái online ngay khi kết nối
        client.publish(TOPIC_STATUS, json.dumps({
            "id": CLIENT_ID,
            "status": "online"
        }), qos=2, retain=True)
        print("📡 Đã gửi trạng thái online (retain, QoS=2)")
    else:
        print(f"❌ Kết nối thất bại, mã lỗi: {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ Mất kết nối đột ngột, sẽ gửi LWT nếu có.")

# ======= Tạo client MQTT =======
client = mqtt.Client(client_id=CLIENT_ID)

# Thiết lập LWT (Last Will and Testament)
lwt_payload = json.dumps({
    "id": CLIENT_ID,
    "status": "offline"
})
client.will_set(TOPIC_STATUS, lwt_payload, qos=2, retain=True)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# ======= Kết nối đến broker =======
print("🔌 Đang kết nối đến broker...")
client.connect(BROKER, PORT, keepalive=60)

# ======= Bắt đầu vòng lặp mạng =======
client.loop_start()


# Gửi dữ liệu trong vòng 60 giây
start_time = time.time()
while True:
    elapsed = time.time() - start_time
    if elapsed >= 60:
        print("⏱ Đã 60 giây — dừng gửi dữ liệu.")
        break

    # Tạo dữ liệu giả lập
    temperature = round(random.uniform(20.0, 40.0), 2)
    humidity = round(random.uniform(30.0, 90.0), 2)
    # Timestamp local (năm-tháng-ngày giờ:phút:giây)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "id": CLIENT_ID,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": timestamp
    }
    payload = json.dumps(data)

    # Gửi dữ liệu — QoS = 2, retain = False (dữ liệu dòng thường không cần retain)
    client.publish(TOPIC_SENSOR, payload, qos=2, retain=False)
    print("📤 Gửi dữ liệu:", payload)

    time.sleep(1)

    # Sau khi hết 60 giây, gửi trạng thái offline cuối cùng
offline_payload = json.dumps({
    "id": CLIENT_ID,
    "status": "offline"
})
client.publish(TOPIC_STATUS, offline_payload, qos=2, retain=True)
print("📡 Gửi trạng thái offline cuối cùng (retain, QoS=2)")

# Đợi chút để broker nhận
time.sleep(1)

client.loop_stop()
client.disconnect()
print("🚪 Đã ngắt kết nối an toàn.")
