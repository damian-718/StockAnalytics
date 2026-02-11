from pyspark.sql.types import *

# this is what a candle will look like inside spark
# nothing to do with table creation (candle model), this is for sparks dataframe engine
# note: this is currently not being used because the db already enforces schema when ingested. this would be used when reading from a csv or json etc...
# just here for convention atm...
candle_schema = StructType([
    StructField("symbol", StringType(), False),
    StructField("interval", StringType(), False),
    StructField("timestamp", TimestampType(), False),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", DoubleType()),
])