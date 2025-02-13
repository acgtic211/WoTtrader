import os
import time
import requests
import json

# Base folder where the Node folders are located
base_folder = "."

# List of node folders and their corresponding URLs
nodes = {
    "Node1": "http://localhost:3021/api/td",
    "Node2": "http://localhost:3022/api/td",
    "Node3": "http://localhost:3023/api/td",
    "Node4": "http://localhost:3024/api/td",
    "Node5": "http://localhost:3025/api/td",
    "Node6": "http://localhost:3026/api/td",
    "Node7": "http://localhost:3027/api/td",
    "Node8": "http://localhost:3028/api/td",
    "Node9": "http://127.0.0.1:9000/api/things",
    "Node10": "http://127.0.0.1:8081/things"
}


def post_document(url, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        document = json.load(file)
    
    response = requests.post(url, json=document)
    if response.status_code == 201:
        print(f"Successfully posted {filepath} to {url}")
        #Time for WotHive, without the sleep it crashes
        time.sleep(5)
    else:
        print(f"Failed to post {filepath} to {url}: {response.status_code} - {response.text}")

# Loop through the node folders and post the documents
for node, url in nodes.items():
    folder = os.path.join(base_folder, node)
    if os.path.exists(folder) and os.path.isdir(folder):
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                post_document(url, filepath)