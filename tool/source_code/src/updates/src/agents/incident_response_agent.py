import openai
import zmq
import pika
import json

class IncidentResponseAgent:
    def __init__(self, context, channel):
        self.context = context
        self.channel = channel
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.channel.queue_declare(queue='incident_queue')
        self.channel.basic_consume(queue='incident_queue', on_message_callback=self.on_message, auto_ack=True)

    def respond_to_threat(self, threat_data):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=f"Respond to the following threat data:\n{threat_data}\nResponse:",
            max_tokens=50
        )
        response_action = response.choices[0].text.strip()
        return response_action

    def on_message(self, ch, method, properties, body):
        message = json.loads(body)
        threat_data = message.get("threat_data")
        if threat_data:
            response_action = self.respond_to_threat(threat_data)
            self.send_message(json.dumps({"response_action": response_action}))

    def send_message(self, message):
        self.socket.send_string(message)
        self.channel.basic_publish(exchange='',
                                   routing_key='incident_queue',
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

    agent = IncidentResponseAgent(context, channel)
    agent.start()
