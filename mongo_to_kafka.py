import time
from pyspark.shell import spark
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import from_json, to_json, explode, struct
import os

import findspark
findspark.init()
findspark.find()

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0,org.apache.kafka:kafka-clients:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.apache.commons:commons-pool2:2.11.1,org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.4.0 pyspark-shell'

spark = SparkSession \
    .builder \
    .appName("tweetsstream") \
    .getOrCreate()

connection_string = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.2'

mongo_df = spark.read \
    .format("mongodb") \
    .option("spark.mongodb.connection.uri", connection_string) \
    .option("spark.mongodb.database", "tweetsDB") \
    .option("spark.mongodb.collection", "tweets") \
    .load()

# Convert all columns to a struct column
struct_df = mongo_df.select(struct(mongo_df.columns).alias("data"))

# Convert struct column to JSON and rename to "value"
json_df = struct_df.select(to_json("data").alias("value"))

kafka_bootstrap_servers = "127.0.0.1:9092"
kafka_topic = "twitterstream"

# save to kafka each 15 seconds with 10000 rows

while True:

    df1 = json_df.limit(10000)
    json_df = json_df.subtract(df1)

    df1 \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("topic", kafka_topic) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .save()
    
    time.sleep(15)