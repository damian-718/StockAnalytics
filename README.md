Each file includes many comments mainly for my own understanding. Goal was to learn how to implement a full data pipeline as close to a real world example as possible locally.
Project is intergated with docker for setup ease. Will download postgres into a docker container, fetch candle data via Coinbase API calls and populate postgres. Then transfer data into S3, as well as AI analysis and computations.

Currently only supports BTC, more to come soon...

Prereqs:

1) Docker Desktop installed
2) AWS account and S3 bucket paths
3) Anthropic API key
4) Populate .env_example file with your paths and information, then rename to .env

How to run:

1) Build and run application
    1) cd docker
    2) docker-compose build
    3) docker-compose up -d postgres
    4) docker-compose run --rm init-db
    5) docker-compose run --rm ingest-candles

2) Now postgres inside docker should have candle data. Services available:
    - 'ingest-candles' - Fetch data from Coinbase API
    - 'process-candles' - Transform raw data with Spark into S3 (will be extending functionality for validity and cleaning)
    - 'compute-metrics' - Calculate technical indicators, upload to S3
    - 'generate-report' - AI-powered market summary
    - 'postgres' - Database storage
    - 'init-db' - One time command needed on first run to initialize tables in Postgres

3) To run services, simply do docker-compose run --rm 'service-name'. Note: -- rm indicates one-off task. Container is no longer needed once task is done so its shut off.

Notes:

goal is an api call is made to coinbase, data is ingested via cron job every minute (variable up to you)and uploaded to postgres. spark for ingestion is overkill. but then every hour or so, spark will send data (batch job) from postgres to s3.
batch job will grab 1m, 5m,15m, and 1 hr candles and group accordingly.

each script is its own flask app.

When spark job runs, it will search through the spark_job_offsets table. Each job has a row. For example, we have have process_candles.py and compute_metrics.py, each a job. Each job gets a corresponding row in the postgres DB table. The 2 columns would be [job_name, last_processed_ts]. So everytime we run process_candles.py, it will go into the table, look for the row where job_name=process_candles, check the ts and update it.
Keep in mind, it will first validate if the ts was already processed, by checking if rows in the market_candles table have ts > last_processed_ts. If so, the latest_processed_ts in the offsets table gets updated.

Next Steps: 

ensure idempotency on metrics, and metrics on existing data, new data only
fix issue where postgres doesnt enforce timestamp offset for process_candles

Some ideas:

1) Do anomoly detection. As metrics are computed, flag high volatility. If volatility is x amount greater than average, flag it via spark and then claude can read and interpret the data.
With spark streaming, this would require a Claude API call every batch computation.