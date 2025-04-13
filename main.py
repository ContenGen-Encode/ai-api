import os
import pika
import caller
import json

# Connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE")

def callback(ch, method, properties, body):
    jsonObj = json.loads(body)
    print(f"Received message: {jsonObj}")

    #[audioRes, subRes] = caller.generate(jsonObj)
    res = caller.generate(jsonObj)

    # Publish message to the exchange
    message = {
    "audio": res[0],
    "subtitle": res[1]
    }
    
    publishMessage(json.dumps(message), jsonObj["UserId"])

def main():
    # Connect to RabbitMQ server
    global channel

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=pika.PlainCredentials(os.getenv("RABBITMQ_USER"), os.getenv("RABBITMQ_PASS"))))
    channel = connection.channel()

    # Make sure the queue exists
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Make sure the exchange exists
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    # Subscribe to the queue
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=True  # Change to False if you want to manually ack after processing
    )

    print(f"[*] Waiting for messages in {QUEUE_NAME}...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        print("[*] Stopping consumption...")
        connection.close()


def publishMessage(body, userId):
    # Publish a message to the exchange
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=userId,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    print(f" [x] Sent '{body}'")

main()