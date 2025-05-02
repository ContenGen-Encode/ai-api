import asyncio
import os
import aio_pika
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

async def callback(ch, message):
    async with message.process():
        userId = ""
        try: 
            jsonObj = json.loads(message.body)
            print(f"\n\nReceived message: {json.loads(jsonObj)['ProjectId']}")

            
            userId = json.loads(jsonObj)["UserId"]
            #[audioRes, subRes] = caller.generate(jsonObj)
            res =  await caller.generate(jsonObj)
            
            # Publish message to the exchange
            if "error" in res:
                message = {
                    "error": str(res["error"]),
                    "message": str(res["message"])
                }
                
                await publishMessage(ch, bytes(json.dumps(message), encoding="utf8"), userId)

            else:
                res_dict = json.loads(res["response"].text)
                message = {
                    "id": res_dict["projectId"],    
                }

                await publishMessage(ch, bytes(json.dumps(message), encoding="utf8"), userId)
        except Exception as e:
            print(e)
            await publishMessage(ch, bytes(json.dumps({
                "error": "something wong",
                "message": "this is unexpected"
            }), encoding="utf8"), userId)



async def main(loop):
    # Connect to RabbitMQ servera
    user = os.getenv("RABBITMQ_USER")
    pwd = os.getenv("RABBITMQ_PASS") 
    connectionString = f"amqp://{user}:{pwd}@{RABBITMQ_HOST}/"
    connection: aio_pika.RobustConnection = await aio_pika.connect_robust(connectionString,loop=loop)

    async with connection:
        channel: aio_pika.abc.AbstractChannel = await connection.channel()

        exchange = await channel.declare_exchange(EXCHANGE_NAME, auto_delete=False, type="topic", durable=True)

        queue = await channel.declare_queue(QUEUE_NAME, auto_delete=False, durable=True)

        print(f"[*] Waiting for messages in {QUEUE_NAME}...") 
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                asyncio.create_task(callback(channel, message))

        
    print("[*] Stopping consumption...")


async def publishMessage(ch: aio_pika.abc.AbstractChannel, body, userId):
    # Publish a message to the exchange

    await ch.default_exchange.publish(
        routing_key  = userId,
        message      = aio_pika.Message(
            body=body
        ),
        # properties   = pika.BasicProperties(delivery_mode = 2,)
    )

    print(f" [x] Sent '{body}'")

# Unit testing i think
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop=loop))
    loop.close()