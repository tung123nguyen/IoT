import pika

# AMQP URL từ CloudAMQP
cloudamqp_url = 'amqps://igqwcvju:qb3AtlQoKdnPar01esAuUWS4LZTpXk7y@fuji.lmq.cloudamqp.com/igqwcvju'

# 1. Kết nối tới CloudAMQP
params = pika.URLParameters(cloudamqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# 2. Khởi tạo queue (nếu chưa tồn tại)
channel.queue_declare(queue='hello')

# 3. Callback function khi nhận message
def callback(ch, method, properties, body):
    print(f"[x] Received: {body.decode()}")

# 4. Đăng ký consumer
channel.basic_consume(queue='hello',
                      on_message_callback=callback,
                      auto_ack=True)  # auto_ack=True: thông báo message đã được xử lý

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
