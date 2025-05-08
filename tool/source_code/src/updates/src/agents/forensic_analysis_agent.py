import openai
import zmq
import pika
import json

class ForensicAnalysisAgent:
    def __init__(self, context, channel):
        self.context = context
        self.channel = channel
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5558")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.channel.queue_declare(queue='forensic_queue')
        self.channel.basic_consume(queue='forensic_queue', on_message_callback=self.on_message, auto_ack=True)

    def perform_analysis(self, compromised_system_data):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=f"Perform forensic analysis on the following compromised system data:\n{compromised_system_data}\nAnalysis:",
            max_tokens=100
        )
        analysis_result = response.choices[0].text.strip()
        return analysis_result

    def on_message(self, ch, method, properties, body):
        message = json.loads(body)
        compromised_system_data = message.get("compromised_system_data")
        if compromised_system_data:
            analysis_result = self.perform_analysis(compromised_system_data)
            self.send_message(json.dumps({"analysis_result": analysis_result}))

    def send_message(self, message):
        self.socket.send_string(message)
        self.channel.basic_publish(exchange='',
                                   routing_key='forensic_queue',
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

    agent = ForensicAnalysisAgent(context, channel)
    agent.start()
