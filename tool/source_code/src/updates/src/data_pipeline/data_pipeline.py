import zmq
import pika
import json
import requests

class DataPipeline:
    def __init__(self):
        self.context = zmq.Context()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='data_queue')

    def fetch_threat_intelligence(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def process_data(self, data):
        # Process and normalize data
        processed_data = json.dumps(data)
        return processed_data

    def send_data(self, data):
        # Send data via ZeroMQ
        socket = self.context.socket(zmq.PUB)
        socket.bind("tcp://*:5556")
        socket.send_string(data)

        # Send data via RabbitMQ
        self.channel.basic_publish(exchange='',
                                   routing_key='data_queue',
                                   body=data)

    def run_pipeline(self, url):
        data = self.fetch_threat_intelligence(url)
        if data:
            processed_data = self.process_data(data)
            self.send_data(processed_data)

if __name__ == "__main__":
    pipeline = DataPipeline()
    threat_intelligence_url = "https://example.com/threat_intelligence"
    pipeline.run_pipeline(threat_intelligence_url)
