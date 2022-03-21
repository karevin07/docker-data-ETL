import sys

import pandas as pd
from pyspark.sql import SparkSession

input_file = sys.argv[1]
table_to_write = sys.argv[2]

postgres_jdbc_url = sys.argv[3]
postgres_user = sys.argv[4]
postgres_passwd = sys.argv[5]

spark = (SparkSession
         .builder
         .getOrCreate()
         )

pandasDF = pd.read_csv(input_file)
sparkDF = spark.createDataFrame(pandasDF)

sparkDF.write.format("jdbc") \
    .mode('append') \
    .option("url", postgres_jdbc_url) \
    .option("driver", "org.postgresql.Driver") \
    .option("dbtable", table_to_write) \
    .option("user", postgres_user) \
    .option("password", postgres_passwd) \
    .save()
