import os
import re
import sys
import json


import pandas
import jieba
from pyspark.sql import SparkSession
from pyspark.sql.functions import col



input_file = sys.argv[1]
output_path = sys.argv[2]
title_output = os.path.join(output_path, "output_title.csv")
content_output = os.path.join(output_path, "output_content.csv")


# Create spark session

spark = (SparkSession
         .builder
         .getOrCreate()
         )

sc = spark.sparkContext

jieba.set_dictionary("/home/workspace/data/dict_tw.txt")


def regular(w):
    line = re.findall('[\u4e00-\u9fa5]+', w)
    if len(line) > 0:
        return line


def get_cut(content):
    seg_list = jieba.cut(content, cut_all=True, HMM=True)
    return seg_list


def text_cleaning(paragraph):
    merge_words = []
    words = get_cut(paragraph)
    for w in words:
        if len(w) > 1:
            w = regular(w)
            if w is not None:
                merge_words.extend(w)
    return "\n".join(merge_words)


def main():
    f = open(input_file)
    data = json.load(f)
    newJson = str(data)
    df = spark.read.json(sc.parallelize([newJson]))
    df_title = df.select(
        col("link_id"),
        col("title")
    )
    df_content = df.select(
        col("content"),
        col("link_id")
    ).rdd.map(
        lambda x: (x[0], x[1])
    ).flatMap(
        lambda x: ([(w, x[1]) for w in text_cleaning(x[0]).split("\n")])
    ).map(
        lambda x: (x, 1)
    ).reduceByKey(
        lambda x, y: x + y
    ).map(
        lambda x: (x[0][0], x[0][1], x[1])
    ).toDF(["word", "index", "count"])
    df_title.toPandas().to_csv(title_output, index=False)
    df_content.toPandas().to_csv(content_output, index=False)


main()