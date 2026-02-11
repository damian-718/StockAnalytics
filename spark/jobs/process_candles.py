import os
from spark.spark_session import get_spark
from dotenv import load_dotenv
load_dotenv()

# how spark will read env variables to read from the postgres db
POSTGRES_URL = (
    f"jdbc:postgresql://{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
DB_PROPS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "org.postgresql.Driver",
}

JOB_NAME = "process_candles" # each batch job has its own name (the .py file name). This is for processing candles to S3
S3_PATH = os.getenv("S3_CANDLES_PATH") # the aws S3 path spark uploads to (gets it from .env)


def run():
    spark = get_spark("ProcessCandles")

    # read last processed timestamp
    offset_df = (
        spark.read
        .jdbc( # spark connects to DB via JDBC. Reads entire spark_offsets table
            POSTGRES_URL,
            table="spark_job_offsets",
            properties=DB_PROPS
        )
        .filter(f"job_name = '{JOB_NAME}'") # keep only the row for this specific batch job (process_candles)
    )

    # [0] grabs first and only row. then grabs the column and the only the column labeled "last_processed_ts". the row is [job_name][last_processed_ts]
    last_ts = offset_df.collect()[0]["last_processed_ts"] #.collect() is a action which brins spark back to who called it (driver) and converts dataframe to python list of rows.

    # read only NEW candles
    candles_df = (
        spark.read
        .jdbc(
            POSTGRES_URL,
            table="market_candles",
            properties=DB_PROPS
        )
        .filter(f"timestamp > TIMESTAMP '{last_ts}'")
    )
    if candles_df.count() == 0: # if no data was added to DB after existing offset
        print("No new data — exiting")
        spark.stop()
        return


    # write to S3 (append is now safe)
    (
        candles_df
        .repartition("symbol", "interval")
        .write
        .mode("append")
        .partitionBy("symbol", "interval")
        .parquet(S3_PATH)
    )

    # compute new high-water mark. high water mark is when spark will compute the maximum event time. in this case scan the new rows and get the row with the maximum timestamp.
    # .agg(timestamp, max) does a computation where it returns only the timestamp column and only the max. then with the new dataframe (1 row) get the one and only column
    max_ts = candles_df.agg({"timestamp": "max"}).collect()[0][0] #[0][0] means take the first row, then the first column. [0][0] is just how we access first row first column in dataframes.

    # persist new offset
    # important note: every batch job has one row. so one row for process_candles, one row for compute_metrics
    # every batch job will update the relevant row with the new offset
    update_df = spark.createDataFrame(
        [(JOB_NAME, max_ts)],
        ["job_name", "last_processed_ts"] # the columns in each row. each batch job gets a row
    )

    (
        update_df
        .write
        .mode("overwrite")
        .jdbc(POSTGRES_URL, "spark_job_offsets", properties=DB_PROPS) # spark_job_offsets is the name of the table in the DB
    )

    spark.stop()

# means you can only run this script from this file
if __name__ == "__main__":
    run()