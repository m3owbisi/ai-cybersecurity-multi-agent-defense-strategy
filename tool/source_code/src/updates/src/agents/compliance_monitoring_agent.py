import zmq
import pika
import json

class ComplianceMonitoringAgent:
    def __init__(self, context, channel):
        self.context = context
        self.channel = channel
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5558")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

        self.channel.queue_declare(queue='compliance_queue')
        self.channel.basic_consume(queue='compliance_queue', on_message_callback=self.on_message, auto_ack=True)

    def monitor_compliance(self, system_data):
        # Placeholder for compliance monitoring logic
        compliance_status = "Compliant" if "security_policy" in system_data else "Non-Compliant"
        return compliance_status

    def on_message(self, ch, method, properties, body):
        message = json.loads(body)
        system_data = message.get("system_data")
        if system_data:
            compliance_status = self.monitor_compliance(system_data)
            self.send_message(json.dumps({"compliance_status": compliance_status}))

    def send_message(self, message):
        self.socket.send_string(message)
        self.channel.basic_publish(exchange='',
                                   routing_key='compliance_queue',
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

    agent = ComplianceMonitoringAgent(context, channel)
    agent.start()
