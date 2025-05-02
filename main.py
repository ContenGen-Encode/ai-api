import os
import pika
import caller
import json
import threading
import asyncio
import sys
import aio_pika
from dotenv import load_dotenv
load_dotenv()
# Connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE")

def callback(ch, method, properties, body):
    userId = ""
    try: 
        jsonObj = json.loads(body)
        print(f"\n\nReceived message: {json.loads(jsonObj)['ProjectId']}")

        
        userId = json.loads(jsonObj)["UserId"]
        #[audioRes, subRes] = caller.generate(jsonObj)
        res = caller.generate(jsonObj)
        
        # Publish message to the exchange
        if "error" in res:
            message = {
                "error": str(res["error"]),
                "message": str(res["message"])
            }
            
            publishMessage(json.dumps(message), userId)

        else:
            res_dict = json.loads(res["response"].text)
            message = {
                "id": res_dict["projectId"],    
            }

            publishMessage(json.dumps(message), userId)
    except Exception as e:
        print(e)
        publishMessage(json.dumps({
            "error": "something wong",
            "message": "this is unexpected"
        }), userId)


# async def consume():
#     # Connect to RabbitMQ server
#     global channel

#     try:
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=RABBITMQ_HOST,
#                 credentials=pika.PlainCredentials(
#                     os.getenv("RABBITMQ_USER"),
#                     os.getenv("RABBITMQ_PASS")
#                 )
#             )
#         )
#     except Exception as e:
#         print("Failed to connect to reabbitmq")
#         return asyncio.create_task(asyncio.sleep(5))

#     channel = connection.channel()

#     # Make sure the queue exists
#     channel.queue_declare(queue=QUEUE_NAME, durable=True)

#     # Make sure the exchange exists
#     channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

#     # Subscribe to the queue
#     channel.basic_consume(
#         queue=QUEUE_NAME,
#         on_message_callback=callback,
#         auto_ack=True  # Change to False if you want to manually ack after processing
#     )
    
#     print(f"[*] Waiting for messages in {QUEUE_NAME}...")

#     try:
#         await channel.start_consuming()
#     except KeyboardInterrupt:
#         await channel.stop_consuming()
#     finally:
#         print("[*] Stopping consumption...")
#         await connection.close()

async def consume():
    while True:
        try:
            connection = await aio_pika.connect_robust(
                host=RABBITMQ_HOST,
                login=os.getenv("RABBITMQ_USER"),
                password=os.getenv("RABBITMQ_PASS"),
                timeout=30,
                client_properties={"connection_name": "my_consumer"}
            )
            
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                
                exchange = await channel.declare_exchange(
                    EXCHANGE_NAME,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                await queue.bind(exchange, routing_key="#")
                
                print(f"[*] Waiting for messages in {QUEUE_NAME}...")
                await queue.consume(callback)
                
                await asyncio.Future()  # Run forever

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Connection error: {str(e)}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)



def main(): 
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(consume())
        

def publishMessage(body, userId):
    # Publish a message to the exchange
    channel.basic_publish(
        exchange     = EXCHANGE_NAME,
        routing_key  = userId,
        body         = body,
        properties   = pika.BasicProperties(delivery_mode = 2,)
    )

    print(f" [x] Sent '{body}'")

main()

#Unit testing i think
# if __name__ == "__main__":
#     smth = json.dumps({"UserId": "1", "Prompt": "Write me a story", "Tone": "funny"})
#     smth = json.dumps(smth)
#     callback(None, None, None, smth)