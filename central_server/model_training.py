import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.models import load_model

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from keras.layers import Dropout
from numpy import array
from keras.preprocessing.text import one_hot
from keras_preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

import pickle
import json

class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions

"""## Download and prepare dataset"""

finished=False
vocab_size = 60
df = pd.read_csv("mainSimulationAccessTraces.csv")
df = df[~df['destinationServiceType'].isin(['/batteryService', '/thermostat', '/movementSensor', '/sensorService'])] # remove rows where destinationServiceType is /batteryService, /thermostat or /movementSensor
conditions = [
    df['destinationLocation'].isin(['Bedroom', 'room_10']),
    df['destinationLocation'].isin(['Dinningroom', 'Livingroom','Entrance']),
    df['destinationLocation'].isin(['Garage', 'Watterroom', 'room_1', 'room_7']),
    df['destinationLocation'].isin(['BedroomParents', 'BedroomChildren', 'Bathroom', 'Showerroom']),
    df['destinationLocation'].isin(['Kitchen', 'room_2']),
    df['destinationLocation'].isin(['room_6', 'room_8', 'room_3', 'room_4', 'room_9', 'room_5']) #Me falta preparar esto en la base de datos
]
choices = ['http://127.0.0.1:3021', 'http://127.0.0.1:3023', 'http://127.0.0.1:3025', 'http://127.0.0.1:3027', 'http://127.0.0.1:3029', 'http://127.0.0.1:7999']
df['node'] = np.select(conditions, choices, default='')
data = df[['destinationServiceType', 'destinationLocation', 'operation']]
sentences = []
for service, location, operation in data.itertuples(index=False):
  sentences.append("I need " + service[1:] + " in " + location)
encoder = LabelEncoder()
labels = encoder.fit_transform(df['node'])

encoded_docs = [one_hot(d, vocab_size) for d in sentences]
print(encoded_docs)

max_length = 5
padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
print(padded_docs)

#np.random.shuffle(padded_docs)
#np.random.shuffle(labels)
x_train, x_val, y_train, y_val = train_test_split(padded_docs, labels, test_size=0.25, random_state=42)

"""## Create classifier model using transformer layer

Transformer layer outputs one vector for each time step of our input sequence.
Here, we take the mean across all time steps and
use a feed forward network on top of it to classify text.
"""

embed_dim = 64  # Embedding size for each token
num_heads = 4  # Number of attention heads
ff_dim = 64  # Hidden layer size in feed forward network inside transformer

inputs = layers.Input(shape=(max_length,))
embedding_layer = TokenAndPositionEmbedding(max_length, vocab_size, embed_dim)
x = embedding_layer(inputs)
transformer_block = TransformerBlock(embed_dim, num_heads, ff_dim)
x = transformer_block(x)
x = layers.GlobalAveragePooling1D()(x)
# x = layers.Dropout(0.1)(x)
x = layers.Dropout(0.1)(x)
x = layers.Dense(256, activation="relu")(x)
# x = layers.Dropout(0.1)(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(128, activation="relu")(x)
# x = layers.Dropout(0.1)(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(64, activation="relu")(x)
# x = layers.Dropout(0.1)(x)
x = layers.Dropout(0.3)(x)
#x = layers.Dense(16, activation="relu")(x)
x = layers.Dense(32, activation="relu")(x)
# x = layers.Dropout(0.1)(x)
x = layers.Dropout(0.1)(x)
outputs = layers.Dense(len(set(labels)), activation="softmax")(x)

model = keras.Model(inputs=inputs, outputs=outputs)
print(model.summary())

"""## Train and Evaluate"""

model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)
history = model.fit(
    x_train, y_train, batch_size=128, epochs=12, validation_data=(x_val, y_val)
)

#pd.DataFrame(history.history).plot(figsize=(8,5))
#plt.grid(True)
#plt.gca().set_ylim(0,1)
#plt.show()
loss, accuracy = model.evaluate(x_train, y_train, verbose=0)
print('Accuracy: %f' % (accuracy*100))
finished=True
