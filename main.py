import asyncio
import os
import caller
import json
import aio_pika
from aio_pika.message import AbstractIncomingMessage
from dotenv import load_dotenv

load_dotenv(override=True)

# Connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE")
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE")

async def callback(exchange, message: AbstractIncomingMessage):
    async with message.process():
        userId = ""
        try: 
            jsonStr = json.loads(message.body)
            jsonObj = json.loads(jsonStr)
            print(jsonObj)
            print(f"\n\nReceived message: {jsonObj['ProjectId']}")

            
            userId = jsonObj["UserId"]

            print(f"UserId: {userId}")

            res =  await caller.generate(jsonObj)
            
            # Publish message to the exchange
            if "error" in res:
                message = {
                    "error": str(res["error"]),
                    "message": str(res["message"])
                }
                
                await publishMessage(exchange, message, userId)

            else:
                res_dict = res["response"]
                message = {
                    "id": res_dict["projectId"],    
                }

                await publishMessage(exchange, message, userId)
        except Exception as e:
            print(e)
            await publishMessage(exchange, {
                "error": "something wong",
                "message": "this is unexpected"
            }, userId)



async def main(loop):
    # Connect to RabbitMQ server
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
                asyncio.create_task(callback(exchange, message))

        
    print("[*] Stopping consumption...")


async def publishMessage(exchange: aio_pika.abc.AbstractExchange, body, userId):
    # Publish a message to the exchange

    await exchange.publish(
        routing_key  = userId,
        message      = aio_pika.Message(
            body=json.dumps(body).encode()
        ),
    )

    print(f" [x] Sent '{body}'")

# Unit testing i think
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop=loop))
    loop.close()