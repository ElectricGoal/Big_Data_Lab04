# BigData_Lab04

## Cài đặt mongoDB trên Ubuntu

```
sudo apt-get install gnupg

curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org
```

Chạy mongoDB trên terminal

```
sudo systemctl start mongod

# Chay lenh nay de kiem tra mongoDB co khoi dong chua
sudo systemctl status mongod

```

## Cài đặt Spark

Tải Spark tại link: https://www.apache.org/dyn/closer.lua/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz

Giải nén và chuyển vào thư mục Home

Đổi tên thành `Spark`

Mở terminal và chạy lệnh

```
nano ~/.bashrc
```

Thêm các dòng sau và thay thế tên username bằng tên user ubuntu

```
export SPARK_HOME=/home/{username}/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
```

Quay lại terminal và chạy lệnh này

```
source ~/.bashrc
```

Kiểm tra Spark có hoạt động chưa

```
spark-submit --version
```

Thêm các file jars

```
cd $SPARK_HOME/jars && wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.1.1/mongo-spark-connector_2.12-10.1.1.jar

cd $SPARK_HOME/jars && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver/3.12.13/mongodb-driver-3.12.13.jar

cd $SPARK_HOME/jars && wget https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/3.12.13/mongo-java-driver-3.12.13.jar

cd $SPARK_HOME/jars && wget https://repo1.maven.org/maven2/org/mongodb/bson/4.9.1/bson-4.9.1.jar
```

## Cài đặt Kafka

Tải Kafka tại link: https://downloads.apache.org/kafka/3.4.0/kafka_2.12-3.4.0.tgz

Giải nén và chuyển vào thư mục Home

Đổi tên thành `Kafka`

Mở terminal và chạy lệnh sau

```
cd /home/{uername}/Kafka

bin/zookeeper-server-start.sh config/zookeeper.properties
```

Để đó và mở một terminal khác và chạy lệnh sau

```
cd /home/{uername}/Kafka

bin/kafka-server-start.sh config/server.properties

```

Để đó và mở một terminal khác và chạy lệnh sau để tạo topic cho Kafka

```
bin/kafka-topics.sh --create --topic twitterstream --bootstrap-server localhost:9092

# verify
bin/kafka-topics.sh --describe --topic twitterstream --bootstrap-server localhost:9092
```

## Chạy chương trình

Mở thư mục code và thực hiện lệnh này

```
python3 data_to_mongo.py
```

Đợi chương trình chạy xong, sau đó mở terminal khác lên và chạy lệnh

```
mongosh
```
để mở mongo shell, tiếp theo chạy các lệnh sau trên mongo shell

```
use tweetsDB

db.tweets.find().count()
```

Nếu thấy giá trị trên terminal bằng với giá trị output của file `data_to_mongo.py` thì là oke


Quay lại thư mục code và chạy lệnh sau để khởi động quá trình đọc dữ liệu từ kafka

```
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 kafka_to_visualize.py
```

Đợi một lúc, mở một terminal khác và chạy lệnh để khởi động quá trình lưu data từ mongo sang kafka

```
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 mongo_to_kafka.py
```

## Thông tin file

- data_to_mongo: Lưu data vào mongoDB

- mongo_to_kafka: Lưu data từ mongoDB sang kafka mỗi 15 giây tối đa 10000 dòng cho đến khi lưu tất cả data trong mongoDB

- kafka_to_visualize: Đọc dữ liệu từ kafka để thực hiện các công việc khác như visualize mỗi 20 gíây

## Cần chỉnh sửa 

Thay đổi hàm **process** trong file `kafka_to_visualize.py` để thực hiện phân tích và trục quan hóa

Ở đây, mình có làm thử đếm số tweets trùng nhau và kết quả in ra trên console khá oke

Giờ đến lượt mọi người làm sao để visualize nó :v

## Note

Mỗi lệnh chạy sẽ in ra trên console rât nhiều dòng nhưng đó không phải lỗi mà là tính năng

Ở lần chạy tiếp theo, chỉ cần dùng lệnh `sudo systemctl start mongod` để khỏi động mongoDB, không cần phải chạy file `data_to_mongo.py` nếu chưa có data trong collection tweets trong database tweetsDB.
