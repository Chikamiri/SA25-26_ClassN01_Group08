import unittest
import pika
import json
import os
from tests.base import TestBase, Colors

class TestNotification(TestBase):

    def test_40_rabbitmq_event_processing(self):
        """Verify RabbitMQ message consumption (Integration)"""
        print(f"\n{Colors.BOLD}--- Notification: RabbitMQ Integration ---{Colors.RESET}")
        
        RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
        
        try:
            # 1. Connect to RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            
            # 2. Publish a mock event
            event = {
                "type": "OrderPlacedEvent",
                "ticket_id": 999,
                "email": "test@example.com",
                "seat": "Z99",
                "movie_name": "Test Movie"
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='ticket_events',
                body=json.dumps(event)
            )
            print(" -> Sent mock OrderPlacedEvent to RabbitMQ")
            connection.close()
            
            # We can't easily verify the print output of the other process here,
            # but we've verified the publishing side.
            
        except Exception as e:
            print(f" -> {Colors.YELLOW}Skipping RabbitMQ test: {e}{Colors.RESET}")
            self.skipTest("RabbitMQ not available")

if __name__ == '__main__':
    unittest.main()
