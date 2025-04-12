import os
import pika

# Connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE")

def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    # publishMessage(body, "#")

def main():
    # Connect to RabbitMQ server
    global channel

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=pika.PlainCredentials(os.getenv("RABBITMQ_USER"), os.getenv("RABBITMQ_PASS"))))
    channel = connection.channel()

    # Make sure the queue exists
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Make sure the exchange exists
    channel.exchange_declare(exchange=QUEUE_NAME, exchange_type='topic', durable=True)

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
        exchange=QUEUE_NAME,
        routing_key=userId,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    print(f" [x] Sent '{body}'")

main()