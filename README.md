Prereqs:
Postgres (psql/PGAdmin) ready to go (locally)
Requirements.txt
S3 Bucket in AWS setup and ready to go
Fill in .env file with your credentials

To run:
each script is its own flask app.

1) Run create_tables.py -> this will create a empty market_candle table in Postgres (locally), this will be populated with candles you query
Then run create_spark_tables.py -> this is a table for spark. It is used to track offset (last timestamp processed) to avoid duplicate jobs and only transfer new data to S3 from Postgres.

2) Run scheduler.py -> this will ingest data NOTE:  python -m ingestion.scheduler is the command to run this
3) Run run.py -> this gets the backend going so you can query Postgres (sample endpoint queries here)
4) Run spark....


currently api call is made to coinbase, data is ingested via cron job every minute (variable up to you)and uploaded to postgres. spark for ingestion is overkill. but then every hour or so, spark will send data (batch job) from postgres to s3.
batch job will grab 1m, 5m,15m, and 1 hr candles and group accordingly.


When spark job runs, it will search through the spark_job_offsets table. Each job has a row. For example, we have have process_candles.py and compute_metrics.py, each a job. Each job gets a corresponding row in the postgres DB table. The 2 columns would be [job_name, last_processed_ts]. So everytime we run process_candles.py, it will go into the table, look for the row where job_name=process_candles, check the ts and update it.
Keep in mind, it will first validate if the ts was already processed, by checking if rows in the market_candles table have ts > last_processed_ts. If so, the latest_processed_ts in the offsets table gets updated.

Setting up S3:

This is designed to upload to s3, so you will need to get setup on AWS.

1) Go to AWS S3 Console and click 'Create Bucket'
2) Name it whatever you want, you use that name in .env. The S3 path should go into the .env file.
3) Region us-east-1

Then you will need to setup your access with 'aws configure' command in terminal. Enter your access key and secret access key.
If you dont have those credentials, you will need to go into AWS Console -> IAM -> Users -> Create User. (IAM manages access to AWS resources.)
Give the user a name and attach the policy 'AmazonS3FullAccess' 
Now Create the access key (command line cli) by clicking on the created user.
Now do AWS Configure and input your credentials. 

spark-submit   --jars $(echo ~/spark-jars/*.jar | tr ' ' ',')   spark/jobs/process_candles.py


export PYTHONPATH="/home/damian/StockAnalytics:$PYTHONPATH"
echo $PYTHONPATH


spark-submit   --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.569   spark/jobs/compute_metrics.py

need to use 3.3.4 jar


next steps: ensure idempotency on metrics, and metrics on existing data, new data only
fix issue where postgres locally doesnt enforce timestamp offset for process_candles