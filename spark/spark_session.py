from pyspark.sql import SparkSession
import os
import glob

# spark entry point
def get_spark(app_name: str = "StockAnalytics"): # note: when process_candles.py is run, it will opverwrrite this str name because its calls this entry point to run the spark session.
    jars = ",".join(glob.glob("/home/damian/spark-jars/*.jar"))
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")  # Use all cores locally
        # Add Postgres + Hadoop AWS + AWS SDK bundles compatible with Spark 3.5.0
        # Include hadoop-client to ensure required Hadoop classes are available
        .config(
            "spark.jars.packages",
            "org.postgresql:postgresql:42.7.3,"
        )
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.jars",jars)
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
        .config("spark.hadoop.fs.s3a.connection.timeout", 60000)  # to debug 60s parse error for hadoop, overwrite preset values
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", 60000)
        .config("spark.hadoop.fs.s3a.socket.timeout", 60000)
        .config("spark.hadoop.fs.s3a.retry.limit", 10)
        .config("spark.hadoop.fs.s3a.attempts.maximum", 10)
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY"))
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )