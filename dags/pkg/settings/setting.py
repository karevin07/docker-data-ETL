from datetime import datetime

# Local path & Remote path.
SRC_FOLDER = '/usr/local/spark/resources'


# ETL Flow
DAY_BEFORE = 7
TRANSFORMATION_INPUT = 'data/input'
TRANSFORMATION_INPUT_FILE = 'input.json'
TRANSFORMATION_OUTPUT = 'data/output'
TRANSFORMATION_OUTPUT_TITLE_FILE = 'word'
TRANSFORMATION_OUTPUT_WORD_FILE = 'title'

SPARK_EXTRA_PATH = 'jars/postgresql-9.4.1207.jar'

# Postgres
POSTGRES_DB = "jdbc:postgresql://postgres/test"
POSTGRES_USER = "test"
POSTGRES_PASSWORD = "postgres"

WORD_TABLE = "word"
TITLE_TABLE = "title"



