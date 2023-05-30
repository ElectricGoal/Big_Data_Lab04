from pymongo import MongoClient
from datasets import load_dataset

dataset = load_dataset("deberain/ChatGPT-Tweets")

connection_string = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.2'

client = MongoClient(connection_string)

db = client["tweetsDB"]

collection = db["tweets"]

data_to_insert = []
batch_size = 1000

for i, data in enumerate(dataset["train"]):
    data_to_insert.append(data)
    
    if len(data_to_insert) == batch_size or i == len(dataset["train"]) - 1:
        collection.insert_many(data_to_insert)
        data_to_insert = []

row_count = collection.count_documents({})
print("Number of rows in the collection:", row_count)