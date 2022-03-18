import os
import re
import sys

import jieba
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col



input_path = sys.argv[1]
input_file = sys.argv[2]
output_path = sys.argv[3]
transformation_jar = sys.argv[4]
output_word_path = sys.argv[5]
output_title_path = sys.argv[6]

# Create spark session

spark = (SparkSession
         .builder
         .config("spark.driver.extraClassPath", transformation_jar)
         .getOrCreate()
         )


def regular(w):
    line = re.findall('[\u4e00-\u9fa5]+', w)
    if len(line) > 0:
        return line


def get_cut(content):
    seg_list = jieba.cut(content, cut_all=False, HMM=True)
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
    df = spark.read.json(os.path.join(input_path, input_file))
    titleOutput = os.path.join(output_path, output_title_path)
    wordOutput = os.path.join(output_path, output_word_path)
    titleDf = df.select(
        lit("link_id"),
        col("title")
    )
    wordDf = df.select(
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

    titleDf.write.csv(titleOutput, header=True)
    wordDf.write.csv(wordOutput, header=True)


main()