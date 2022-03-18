from datetime import datetime

# Local path & Remote path.
SRC_FOLDER = '/home/workspace'


# ETL Flow
DAY_BEFORE = 7
TRANSFORMATION_INPUT = 'data/input'
TRANSFORMATION_INPUT_FILE = 'input.json'
TRANSFORMATION_OUTPUT = 'data/output'
TRANSFORMATION_OUTPUT_TITLE_FILE = 'output_title.csv'
TRANSFORMATION_OUTPUT_WORD_FILE = 'output_content.csv'

SPARK_EXTRA_PATH = 'jars/postgresql-9.4.1207.jar'

# Postgres
POSTGRES_DB = "jdbc:postgresql://postgres/test"
POSTGRES_USER = "test"
POSTGRES_PASSWORD = "postgres"

WORD_TABLE = "word"
TITLE_TABLE = "title"



