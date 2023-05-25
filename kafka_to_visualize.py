from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import from_json, to_json, explode, struct

# Function to process the data
def process(batch_df, batch_id):
    print(f"Batch ID: {batch_id}")
    batch_df.show(truncate=False)
    batch_df.groupBy("Tweet").count().show(truncate=False)

spark = SparkSession.builder.appName("kafka_consumer").getOrCreate()

kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "twitterstream"

kafka_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "earliest") \
    .load()

kafka_stream_value = kafka_stream.selectExpr("CAST(value AS STRING)")

schema = StructType([
    StructField("_id", StringType(), True),
    StructField("Date", StringType(), True),
    StructField("Tweet", StringType(), True),
    StructField("Url", StringType(), True),
    StructField("User", StringType(), True),
    StructField("UserCreated", StringType(), True),
    StructField("UserVerified", StringType(), True),
    StructField("UserFollowers", StringType(), True),
    StructField("UserFriends", StringType(), True),
    StructField("Retweets", StringType(), True),
    StructField("Likes", StringType(), True),
    StructField("Location", StringType(), True),
    StructField("UserDescription", StringType(), True)
])


parsed_df = kafka_stream_value.withColumn("value", from_json("value", schema))
res_df = parsed_df.select("value.*")

# Perform further processing on the streaming data
query = res_df.writeStream.trigger(processingTime='20 seconds').foreachBatch(process).start()

# Start the streaming context
# kafka_stream_value.start()
query.awaitTermination()
