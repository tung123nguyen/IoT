import pika

# AMQP URL từ CloudAMQP
cloudamqp_url = 'amqps://igqwcvju:qb3AtlQoKdnPar01esAuUWS4LZTpXk7y@fuji.lmq.cloudamqp.com/igqwcvju'

# 1. Kết nối tới CloudAMQP
params = pika.URLParameters(cloudamqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# 2. Khởi tạo queue (nếu chưa tồn tại)
channel.queue_declare(queue='hello')

# 3. Gửi message
message = "Hello from CloudAMQP Tung!"
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)

print(f"[x] Sent '{message}'")

# 4. Đóng kết nối
connection.close()
