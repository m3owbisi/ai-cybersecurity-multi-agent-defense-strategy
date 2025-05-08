import openai
import zmq
import pika
import json

class BehavioralAnalysisAgent:
    def __init__(self, context, channel):
        self.context = context
        self.channel = channel
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5558")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.channel.queue_declare(queue='behavioral_queue')
        self.channel.basic_consume(queue='behavioral_queue', on_message_callback=self.on_message, auto_ack=True)

    def analyze_behavior(self, behavior_data):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=f"Analyze the following user and system behavior data for anomalies:\n{behavior_data}\nAnomalies:",
            max_tokens=50
        )
        anomalies = response.choices[0].text.strip()
        return anomalies

    def on_message(self, ch, method, properties, body):
        message = json.loads(body)
        behavior_data = message.get("behavior_data")
        if behavior_data:
            anomalies = self.analyze_behavior(behavior_data)
            self.send_message(json.dumps({"anomalies": anomalies}))

    def send_message(self, message):
        self.socket.send_string(message)
        self.channel.basic_publish(exchange='',
                                   routing_key='behavioral_queue',
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

    agent = BehavioralAnalysisAgent(context, channel)
    agent.start()
