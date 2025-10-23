import streamlit as st
import paho.mqtt.client as mqtt
import threading
import json
import time

# =========================
# CẤU HÌNH MQTT
# =========================
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_STATUS = "mqtt_chat/status"
TOPIC_GLOBAL = "mqtt_chat/global"
TOPIC_PRIVATE = "mqtt_chat/private/"
KEEP_ALIVE = 60

# =========================
# KHỞI TẠO SESSION STATE
# =========================
defaults = {
    "connected": False,
    "my_id": "",
    "online_users": set(),
    "messages": [],
    "current_chat": "global",
    "mqtt_client": None,
    "msg_input": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# =========================
# CÁC HÀM MQTT
# =========================
def send_status(client, user_id, status):
    """Gửi trạng thái online/offline."""
    payload = json.dumps({"user_id": user_id, "status": status})
    client.publish(TOPIC_STATUS, payload, qos=1, retain=True)


def send_message(client, sender, receiver, message, is_global=False):
    """Gửi tin nhắn."""
    payload = json.dumps({
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S")
    })
    topic = TOPIC_GLOBAL if is_global else f"{TOPIC_PRIVATE}{receiver}"
    client.publish(topic, payload, qos=1)


# =========================
# CALLBACK MQTT
# =========================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC_STATUS)
        client.subscribe(TOPIC_GLOBAL)
        client.subscribe(f"{TOPIC_PRIVATE}{st.session_state.my_id}")
        send_status(client, st.session_state.my_id, "online")
    else:
        st.error("❌ Kết nối MQTT thất bại!")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except:
        return

    topic = msg.topic

    if topic == TOPIC_STATUS:
        user_id = payload.get("user_id")
        status = payload.get("status")

        if status == "online":
            st.session_state.online_users.add(user_id)
        elif status == "offline":
            st.session_state.online_users.discard(user_id)

    else:
        st.session_state.messages.append(payload)


# =========================
# GIAO DIỆN STREAMLIT
# =========================
st.title("💬 Ứng dụng Chat MQTT")

# Nếu chưa kết nối
if not st.session_state.connected:
    user_id = st.text_input("🔑 Nhập ID (MSSV):", key="input_id")

    if st.button("🔗 Kết nối"):
        if user_id.strip() == "":
            st.warning("⚠️ Vui lòng nhập ID hợp lệ!")
        else:
            st.session_state.my_id = user_id.strip()

            client = mqtt.Client(client_id=st.session_state.my_id)
            client.on_connect = on_connect
            client.on_message = on_message
            st.session_state.mqtt_client = client

            def mqtt_thread():
                client.connect(BROKER, PORT, KEEP_ALIVE)
                client.loop_forever()

            threading.Thread(target=mqtt_thread, daemon=True).start()

            st.session_state.connected = True
            st.success("✅ Đã kết nối MQTT!")
            st.rerun()

# Nếu đã kết nối
else:
    st.sidebar.header("👥 Người dùng đang online")

    users = sorted(list(st.session_state.online_users))
    if st.session_state.my_id in users:
        users.remove(st.session_state.my_id)

    chat_targets = ["global"] + users
    selected_chat = st.sidebar.radio("Chọn người để chat:", chat_targets)
    st.session_state.current_chat = selected_chat

    st.subheader(f"💭 Đang chat với: {selected_chat}")

    # Hiển thị tin nhắn
    chat_box = st.container()

    messages_to_show = []
    for m in st.session_state.messages:
        if selected_chat == "global" and m.get("receiver") == "global":
            messages_to_show.append(m)
        elif selected_chat != "global":
            if (m.get("sender") == st.session_state.my_id and m.get("receiver") == selected_chat) or \
               (m.get("sender") == selected_chat and m.get("receiver") == st.session_state.my_id):
                messages_to_show.append(m)

    with chat_box:
        for msg in messages_to_show:
            if msg["sender"] == st.session_state.my_id:
                st.markdown(
                    f"<div style='text-align:right; color:blue;'>[{msg['timestamp']}] Tôi: {msg['message']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='text-align:left; color:green;'>[{msg['timestamp']}] {msg['sender']}: {msg['message']}</div>",
                    unsafe_allow_html=True
                )

    # Ô nhập tin nhắn
    st.session_state.msg_input = st.text_input("💬 Nhập tin nhắn", value=st.session_state.msg_input)

    col1, col2 = st.columns([1, 0.3])
    with col1:
        if st.button("📤 Gửi"):
            msg = st.session_state.msg_input.strip()
            if msg:
                send_message(
                    st.session_state.mqtt_client,
                    st.session_state.my_id,
                    selected_chat if selected_chat != "global" else "global",
                    msg,
                    is_global=(selected_chat == "global")
                )
                st.session_state.messages.append({
                    "sender": st.session_state.my_id,
                    "receiver": selected_chat,
                    "message": msg,
                    "timestamp": time.strftime("%H:%M:%S")
                })
                # Xóa nội dung ô nhập tin nhắn mà không gây lỗi
                st.session_state.update({"msg_input": ""})
                st.rerun()

    with col2:
        if st.button("❌ Ngắt kết nối"):
            send_status(st.session_state.mqtt_client, st.session_state.my_id, "offline")
            st.session_state.mqtt_client.disconnect()
            st.session_state.connected = False
            st.session_state.online_users.clear()
            st.session_state.messages.clear()
            st.success("🔌 Đã ngắt kết nối!")
            st.rerun()
