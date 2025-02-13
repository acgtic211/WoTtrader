import heapq
from fastapi import FastAPI, Request
import numpy as np
from numpy import array
import tensorflow as tf
from tensorflow import keras
from keras.preprocessing.text import one_hot
from keras_preprocessing.sequence import pad_sequences
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import model_training


app = FastAPI()
security = HTTPBearer()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    title: str
    base: str


def get_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    if token != "YOUR_TOKEN":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@app.on_event("startup")
def load_model():
    global model
    model = model_training.model

@app.get('/')
def index():
    return {'message': 'This is the homepage of the API '}


@app.get('/predict/{sentence}')
def predict(sentence: str, token: str = Depends(get_token)):
    return {'prediction': sentence}



def get_device(sentence: str, discovery: str):
    pred_name = getRecommendations(sentence, model)
    
    paths_data = read_paths_json('paths.json')

    return {'path': get_best_path(paths_data, "http://" + discovery, pred_name[0][0].split("'")[1], pred_name[0][1].split("'")[1])}

def getRecommendations(sentence, model):
    encoded_docs2 = [one_hot(sentence, 60)]
    padded_docs2 = pad_sequences(encoded_docs2, maxlen=5, padding='post')
    y_pred = model.predict(array(padded_docs2))
    encoder = model_training.encoder

    print(np.argmax(y_pred, axis=1))
    ind=np.argpartition(y_pred[0], -4)[-4:]
    print(ind[np.argsort(-1*y_pred[0][ind])])
    print(y_pred[0][ind[np.argsort(-1*y_pred[0][ind])]])

    results = []
    for sentence in y_pred:
        partialResult = []
        ind=np.argpartition(sentence, -4)[-4:]
        ind=ind[np.argsort(-1*sentence[ind])]
        for result in ind:
          partialResult.append(str(encoder.inverse_transform([result])) + ' (' + str(sentence[result]) + ')')
        results.append(partialResult)
    print(results)
    return results

def get_best_path(paths_data, start, objective1, objective2):
    graph = paths_data.items()
    distances = {}
    # Initialize distances dictionary with node addresses as keys and infinity as values
    for key, value in graph:
        address = value['address']
        distances[address] = float('inf')   
    distances[start] = 0
    previous = {value['address']: None for key, value in graph}
    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == objective1 and previous[objective2] is not None:
            break

        for key, value in graph:
            if value['address'] == current_node:
                for neighbor in value['linkedDiscoveries']:
                    print(f"Neighbor {neighbor}")
                    neighbor_address = neighbor
                    #weight = neighbor['weight']
                    distance = current_distance + 1
                    print(f"Distance {distance}")
                    print(f"Distances {distances}")
                    if distance < distances.get(neighbor_address, float('inf')):
                        distances[neighbor_address] = distance
                        previous[neighbor_address] = current_node
                        heapq.heappush(queue, (distance, neighbor_address))

    path = []
    current_node = objective1
    print(current_node)
    print(previous)
    while current_node != start:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    path2 = []
    current_node = objective2
    print(current_node)
    print(previous)
    while current_node != start:
        path2.append(current_node)
        current_node = previous[current_node]
    path2.reverse()

    return [path, path2]




@app.get('/getPath/{sentence}&{discovery}')
def read_paths_json(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

@app.get('/node')
def get_paths():
    try:
        with open('paths.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {'error': str(e)}