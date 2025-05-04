import pika, json

params = pika.URLParameters('amqps://sbgjbiei:CqT2eyLqJUqMCIKQbISkrQcd18T1pcd-@crow.rmq.cloudamqp.com/sbgjbiei')
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='main')  # Declare the same queue

def publish():
    body = {'product_id': 1, 'likes': 1}
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body))
    print('Message sent:', body)