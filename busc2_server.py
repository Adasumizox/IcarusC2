import asyncio
import argparse
from argparse import RawTextHelpFormatter
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

async def send_single_message(sender, message):
    message = ServiceBusMessage(message)
    await sender.send_messages(message)

async def run_send(message, conn: str, sendqueue: str):
    async with ServiceBusClient.from_connection_string(
        conn_str=conn,
        logging_enable=True) as servicebus_client:

        sender = servicebus_client.get_queue_sender(queue_name=sendqueue)
        async with sender:
            await send_single_message(sender, message)

async def run_receive(conn: str, getqueue: str):
    async with ServiceBusClient.from_connection_string(
        conn_str=conn,
        logging_enable=True) as servicebus_client:

        async with servicebus_client:
            receiver = servicebus_client.get_queue_receiver(queue_name=getqueue)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=5)
                for msg in received_msgs:
                    print(str(msg))
                    await receiver.complete_message(msg)

def main():
    parser = argparse.ArgumentParser(description =
" ____   ____    ____  ____  \n" +
"/ ___| | __ )  / ___||___ \ \n" +
"\___ \ |  _ \ | |      __) |\n" +
" ___) || |_) || |___  / __/ \n" +
"|____/ |____/  \____||_____|\n", formatter_class=RawTextHelpFormatter)

    parser.add_argument("-c", "--conn", type = str, metavar = "conn",
                        required=True)
    parser.add_argument("-gq", "--getqueue", type = str, metavar = "getqueue",
                        required=True)
    parser.add_argument("-sq", "--sendqueue", type = str, 
                        metavar = "sendqueue", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--read", action="store_true", 
                        help = "Read all executed command and output")
    group.add_argument("-s", "--send", type = str, nargs = 1, 
                        metavar = "command", 
                        help = "Pass command to execute on current agent")

    args = parser.parse_args()

    if args.read == True:
        asyncio.run(run_receive(args.conn, args.getqueue))
    elif args.send != None:
        asyncio.run(run_send(args.send[0], args.conn, args.sendqueue))

if __name__ == '__main__':
    main()