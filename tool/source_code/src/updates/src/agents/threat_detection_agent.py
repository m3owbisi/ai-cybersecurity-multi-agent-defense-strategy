import openai
import zmq
import pika
import json

class ThreatDetectionAgent:
    def __init__(self, context, channel):
        self.context = context
        self.channel = channel
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.channel.queue_declare(queue='agent_queue')
        self.channel.basic_consume(queue='agent_queue', on_message_callback=self.on_message, auto_ack=True)

    def analyze_traffic(self, traffic_data):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=f"Analyze the following network traffic data for potential threats:\n{traffic_data}\nThreats:",
            max_tokens=50
        )
        threats = response.choices[0].text.strip()
        return threats

    def on_message(self, ch, method, properties, body):
        message = json.loads(body)
        traffic_data = message.get("traffic_data")
        if traffic_data:
            threats = self.analyze_traffic(traffic_data)
            self.send_message(json.dumps({"threats": threats}))

    def send_message(self, message):
        self.socket.send_string(message)
        self.channel.basic_publish(exchange='',
                                   routing_key='agent_queue',
                                   body=message)

    def start(self):
        while True:
            self.channel.start_consuming()
            message = self.socket.recv_string()
            print(f"Received message: {message}")

if __name__ == "__main__":
    context = zmq.Context()
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    agent = ThreatDetectionAgent(context, channel)
    agent.start()
