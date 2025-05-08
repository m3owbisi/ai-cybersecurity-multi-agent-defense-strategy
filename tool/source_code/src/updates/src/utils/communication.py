import zmq
import pika

class Communication:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='agent_queue')

    def send_message(self, message):
        # Send message via ZeroMQ
        self.socket.send_string(message)

        # Send message via RabbitMQ
        self.channel.basic_publish(exchange='',
                                   routing_key='agent_queue',
                                   body=message)

    def close(self):
        self.socket.close()
        self.context.term()
        self.connection.close()
