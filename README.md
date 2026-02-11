Each file includes many comments mainly for my own understanding. Goal was to learn how to implement a full data pipeline as close to a real world example as possible locally.

Prereqs:

Postgres (psql/PGAdmin) ready to go (locally)
S3 Bucket in AWS setup and ready to go
Fill in .env file with your credentials

Note:
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



next steps: ensure idempotency on metrics, and metrics on existing data, new data only
fix issue where postgres locally doesnt enforce timestamp offset for process_candles

Some ideas:

1) Do anomoly detection. As metrics are computed, flag high volatility. If volatility is x amount greater than average, flag it via spark and then claude can read and interpret the data.
With spark streaming, this would require a Claude API call every batch computation.