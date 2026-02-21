import random
import json
from google.cloud import pubsub_v1

def publish_gps(project_id, topic_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data = {
        "device_id": "device_1",
        "lat": 14.5995 + random.random()/100,
        "lon": 120.9842 + random.random()/100,
        "speed": random.randint(10, 80)
    }
    publisher.publish(topic_path, json.dumps(data).encode("utf-8"))
