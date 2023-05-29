from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import re
from textblob import TextBlob
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

spark = SparkSession.builder.getOrCreate()

def analyze_sentiment(tweet):
    blob = TextBlob(tweet)
    return blob.sentiment.polarity

analyze_sentiment_udf = udf(analyze_sentiment, StringType())

# Remove unwanted components from the "Tweet" column using regex
def clean_tweet(tweet):
    cleaned_text = re.sub(r"@\w+|#[^\s]+|http\S+|[^a-zA-Z0-9\s]", "", tweet)
    return cleaned_text

def sentiment(res_df):
    clean_tweet_udf = udf(clean_tweet, StringType())
    res_df = res_df.withColumn("CleanedTweet", clean_tweet_udf("Tweet"))

    res_df = res_df.withColumn("Sentiment", analyze_sentiment_udf("CleanedTweet"))

    # Define thresholds for negative, positive, and neutral sentiments
    positive_threshold = 0.2
    negative_threshold = -0.2

    visualize_df = res_df
    res_df = res_df.withColumn("Sentiment", when(res_df["Sentiment"] > positive_threshold, "positive").when(res_df["Sentiment"] < negative_threshold, "negative").otherwise("neutral"))

    return res_df, visualize_df

# Function to visualize and save the plot for each batch of data
def visualize_batch(batch_df, batch_id):
    _, visualize_df = sentiment(batch_df)

    # Aggregate the sentiment analysis results over a specific time window
    windowed_df = visualize_df.groupBy(window("Date", "1 minute")).agg(avg("Sentiment").alias("AverageSentiment"))

    # Collect the aggregated data into the driver
    results = windowed_df.collect()

    # Extract the window start time and average sentiment values
    window_starts = [str(row['window']['start']) for row in results]
    sentiment_values = [row['AverageSentiment'] for row in results]

    # Create the plot
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=window_starts, y=sentiment_values)
    plt.xlabel("Time Window")
    plt.ylabel("Average Sentiment")
    plt.title("Sentiment Analysis over Time")
    plt.xticks(rotation=45)

    # Save the plot as an image file
    filename = f"sentiment_analysis_{batch_id}.png"
    plt.savefig(filename)
    plt.close()

# Initialize the SparkSession
spark = SparkSession.builder.appName("kafka_consumer").getOrCreate()

kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "twitterstream"

# Read the streaming data from Kafka
kafka_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "earliest") \
    .load()

# Extract the value from Kafka messages
kafka_stream_value = kafka_stream.selectExpr("CAST(value AS STRING)")

# Define the schema for parsing the JSON data
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

# Parse the streaming data and select the required columns
parsed_df = kafka_stream_value.withColumn("value", from_json("value", schema))
res_df = parsed_df.select("value.*")

# Start the streaming query and process each batch
query = res_df.writeStream.trigger(processingTime='20 seconds').foreachBatch(visualize_batch).start()

# Wait for the streaming query to finish
query.awaitTermination()
