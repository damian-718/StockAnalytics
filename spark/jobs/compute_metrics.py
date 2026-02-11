import os
from spark.spark_session import get_spark
from dotenv import load_dotenv

from pyspark.sql import functions as F
from pyspark.sql.window import Window

load_dotenv()

JOB_NAME = "compute_metrics"

S3_CANDLES_PATH = os.getenv("S3_CANDLES_PATH")
S3_METRICS_PATH = os.getenv("S3_METRICS_PATH")

def run():
    spark = get_spark("ComputeMetrics")

    print(f"Reading raw candles from: {S3_CANDLES_PATH}")

    # 1) READ RAW CANDLES FROM S3 (bronze layer)
    candles_df = spark.read.parquet(S3_CANDLES_PATH)

    # this creates a window for calculations, window for 5min, 15min, 60min. each window has the needed rows, like 5 rows, 15 rows, 60 rows...
    window_5 = ( # 5min window
        Window.partitionBy("symbol", "interval") # parition, in the case of many tickers, organizes each ticker into a table/partition (AAPL group, TSLA group, etc...). Then applied the 5 row window for each group. so get me the last 5 rows up this timestamp for each group.
        .orderBy("timestamp")
        .rowsBetween(-5, 0) # last 5 rows per partition
    )

    window_15 = (
        Window.partitionBy("symbol", "interval")
        .orderBy("timestamp")
        .rowsBetween(-15, 0)
    )

    window_60 = (
        Window.partitionBy("symbol", "interval")
        .orderBy("timestamp")
        .rowsBetween(-60, 0)
    )

    window_ordered = (
        Window.partitionBy("symbol", "interval")
        .orderBy("timestamp")
        # no rowsBetween, lag already knows what to do via "F.lag("close", 1)" down below. a window frame breaks it because now its trying to do something between x rows which makes no sense. 
    )
    
    # the actual calculations on each window above. over means over that window (rows)
    metrics_df = (
        candles_df
        # --- PRICE FEATURES ---
        .withColumn("ma_5", F.avg("close").over(window_5)) # find the average of close of the 5 rows in 5 minute window
        .withColumn("ma_15", F.avg("close").over(window_15)) # find the average of close of the 15 rows in 5 minute window
        .withColumn("ma_60", F.avg("close").over(window_60))

        # --- VOLATILITY FEATURES ---
        .withColumn("vol_5", F.stddev("close").over(window_5)) # devations between values (how spread out prices are within 5 minute window). for reference std = 0 is no volatility.
        .withColumn("vol_15", F.stddev("close").over(window_15))

        # --- MOMENTUM ---
        .withColumn("returns_1",
            (F.col("close") - F.lag("close", 1).over(window_ordered)) / # see the rate of change percentage (momentum) from 1 previous row (aka candle) to this one
            F.lag("close", 1).over(window_ordered)
        )

        # --- VOLUME FEATURES ---
        .withColumn("vol_ma_5", F.avg("volume").over(window_5))
        .withColumn("vol_ma_15", F.avg("volume").over(window_15))

        # --- TREND SIGNAL (simple example) ---
        .withColumn(
            "trend_signal",
            F.when(F.col("ma_5") > F.col("ma_15"), 1) # when 5 minute MA is higher than a longer timeframe, it means bullish
             .when(F.col("ma_5") < F.col("ma_15"), -1)
             .otherwise(0)
        )
    )

    print(f"Writing metrics to: {S3_METRICS_PATH}")

    (
        metrics_df
        .repartition("symbol", "interval")
        .write
        .mode("append")
        .option("mergeSchema", "true")   # new columns get merged into existing schema
        .partitionBy("symbol", "interval")
        .parquet(S3_METRICS_PATH)
    )

    spark.stop()
    print("Compute metrics job complete.")

if __name__ == "__main__":
    run()