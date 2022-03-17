package com.github.data

import com.github.data.utils.SparkSessionWrapper

object transforms extends SparkSessionWrapper {

  def main(args: Array[String]): Unit = {

    val inputFile = args(0)
    val outputPath = args(1)

    val content = {
      spark.sparkContext.textFile(inputFile)
    }

    val wordCount = content.map(
      x => (x, 1)
    ).reduceByKey(
      (a,b) => a + b
    )

    import spark.implicits._

    val df = wordCount.toDF("word", "count")

    df.write.option("header", "true").csv(outputPath)

  }

}
