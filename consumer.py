
import pika, json, os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()

params = pika.URLParameters('amqps://sbgjbiei:CqT2eyLqJUqMCIKQbISkrQcd18T1pcd-@crow.rmq.cloudamqp.com/sbgjbiei')

connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='main')  # Declare the same queue

def callback(ch, method, properties, body):
    print('Received in main')
    id = json.loads(body)
    print(id)
    print('Product likes increased!')

channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)

print('Started Consuming')
channel.start_consuming()
