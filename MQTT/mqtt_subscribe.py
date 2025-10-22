import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import os

# ======= Cấu hình broker và topic =======
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC_STATUS = "iot/Tung20225426/status"   # +: wildcard cho mọi client ID
TOPIC_SENSOR = "iot/Tung20225426/sensor"

# Lưu file log trong thư mục riêng
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Từ điển để quản lý file đang mở theo từng client ID
client_logs = {}

# ======= Callback xử lý khi nhận được message =======
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"\n📩 Nhận tin nhắn từ topic: {topic}")
    print(f"📦 Nội dung: {payload}")

    try:
        data = json.loads(payload)
        client_id = data.get("id", "Unknown")
        status = data.get("status")

        # Nếu là topic trạng thái
        if "status" in topic:
            if status == "online":
                # Mở file log cho client đó
                log_path = os.path.join(LOG_DIR, f"{client_id}_log.txt")
                f = open(log_path, "a", encoding="utf-8")
                client_logs[client_id] = f
                f.write(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} --- Client ONLINE ---\n")
                f.flush()
                print(f"🟢 {client_id} ONLINE — Mở file log: {log_path}")

            elif status == "offline":
                # Đóng file log khi client offline
                if client_id in client_logs:
                    f = client_logs.pop(client_id)
                    f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} --- Client OFFLINE ---\n\n")
                    f.close()
                    print(f"🔴 {client_id} OFFLINE — Đóng file log.")
                else:
                    print(f"⚠️ Nhận offline từ {client_id} nhưng không có file log mở.")

        # Nếu là topic cảm biến
        elif "sensor" in topic:
            if client_id not in client_logs:
                print(f"⚠️ Nhận dữ liệu từ {client_id} nhưng chưa online, bỏ qua.")
                return

            # Ghi dữ liệu cảm biến
            recv_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_time = data.get("timestamp", "N/A")
            temp = data.get("temperature", "N/A")
            hum = data.get("humidity", "N/A")

            log_line = f"{recv_time}\t{send_time}\tTemp: {temp}°C\tHumidity: {hum}%\n"
            f = client_logs[client_id]
            f.write(log_line)
            f.flush()
            print(f"💾 Ghi dữ liệu cho {client_id}: {log_line.strip()}")

    except Exception as e:
        print(f"❌ Lỗi khi xử lý tin nhắn: {e}")

# ======= Callback khi kết nối =======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Kết nối thành công đến broker.")
        # Đăng ký nhận hai loại topic
        client.subscribe(TOPIC_STATUS, qos=2)
        client.subscribe(TOPIC_SENSOR, qos=2)
        print(f"📡 Đăng ký nhận:\n  - {TOPIC_STATUS}\n  - {TOPIC_SENSOR}")
    else:
        print(f"❌ Kết nối thất bại (mã lỗi: {rc})")

# ======= Callback khi mất kết nối =======
def on_disconnect(client, userdata, rc):
    print("⚠️ Mất kết nối đến broker.")
    # Đóng toàn bộ file log đang mở
    for cid, f in client_logs.items():
        f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} --- DISCONNECTED ---\n\n")
        f.close()
        print(f"🔒 Đã đóng file log của {cid}")
    client_logs.clear()

# ======= Tạo client và thiết lập callback =======
client = mqtt.Client(client_id="SubscriberLogger")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# ======= Kết nối đến broker =======
print("🔌 Đang kết nối đến broker...")
client.connect(BROKER, PORT, keepalive=60)

# ======= Bắt đầu vòng lặp =======
client.loop_forever()
