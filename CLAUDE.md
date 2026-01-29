# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight ETL platform that extracts news articles via web crawler, performs word segmentation using jieba, and loads processed data into PostgreSQL. The stack includes Airflow for orchestration, Spark for data transformation, and JupyterLab for development.

## Architecture

The system consists of:
- **Airflow**: Orchestrates ETL workflows
- **Spark Cluster**: Standalone cluster with 1 master and 3 workers for distributed processing
- **PostgreSQL**: Data storage backend
- **JupyterLab**: Interactive development environment

All components run in Docker containers and communicate through a shared network.

## Common Commands

### Building Images

Build all images:
```bash
make build-all
```

Build individual images:
```bash
make build-base          # Base Python image
make build-spark-base    # Spark base image
make build-spark-master  # Spark master node
make build-spark-worker  # Spark worker nodes
make build-airflow       # Airflow webserver
make build-notebook      # JupyterLab
make build-postgres      # PostgreSQL with init scripts
```

Alternative build method for individual components:
```bash
bash build.sh {component_name}  # e.g., bash build.sh airflow
```

### Running Services

Start all services:
```bash
docker-compose up -d
```

Start specific services using Makefile:
```bash
make run-spark     # Start Spark master + workers
make run-airflow   # Start Airflow webserver
make run-notebook  # Start JupyterLab
```

Stop all services:
```bash
make down
```

### Accessing Services

- Airflow UI: http://0.0.0.0:8282
- Spark UI: http://0.0.0.0:8080
- JupyterLab: http://0.0.0.0:8888
- PostgreSQL: localhost:5432

## ETL Pipeline Architecture

### DAG Structure (dags/ETL_demo.py)

The main DAG `etl_flow` runs daily and consists of three sequential stages:

1. **Extract** (dags/pkg/etlflow/Extract.py)
   - Scrapes news from The News Lens politics section
   - Filters articles from the last 7 days (configurable via `DAY_BEFORE`)
   - Saves raw data as JSON to `data/input/input.json`

2. **Transformation** (SubDAG via dags/pkg/etlflow/Transformation.py)
   - Submits Spark job (spark/app/transformation.py)
   - Uses jieba with Traditional Chinese dictionary (`data/dict_tw.txt`)
   - Performs Chinese word segmentation and word count
   - Outputs two CSV files to `data/output/`:
     - `output_title.csv`: Article titles with link IDs
     - `output_content.csv`: Word counts per article

3. **Load** (SubDAG via dags/pkg/etlflow/Load.py)
   - Creates PostgreSQL tables (`title` and `content`)
   - Submits Spark jobs (spark/app/load.py) to write CSVs to PostgreSQL
   - Uses JDBC with PostgreSQL driver from `jars/postgresql-42.3.3.jar`

### Spark Jobs

Spark jobs run via SparkSubmitOperator and require:
- Spark connection configured in Airflow (conn_id: `spark_default`)
- Spark binary path: `/usr/local/spark/bin/spark-submit`
- Application files located in `spark/app/`
- PostgreSQL JDBC driver in `spark/jars/`

### Configuration (dags/pkg/settings/setting.py)

Key settings:
- `SRC_FOLDER`: `/home/workspace` (inside containers)
- `DAY_BEFORE`: 7 (days of news to extract)
- `POSTGRES_JDBC_URL`: `jdbc:postgresql://postgres:5432/airflow`
- Database credentials: airflow/airflow

## Directory Structure

```
/
├── dags/                    # Airflow DAG definitions
│   └── pkg/
│       ├── etlflow/        # ETL stage implementations
│       │   ├── Extract.py
│       │   ├── Transformation.py
│       │   └── Load.py
│       └── settings/       # Configuration
├── spark/
│   ├── app/                # Spark application scripts
│   │   ├── transformation.py
│   │   └── load.py
│   ├── jars/               # JDBC drivers and dependencies
│   └── conf/               # Spark configuration
├── docker/                 # Dockerfiles for all components
│   ├── docker-base/
│   ├── docker-airflow/
│   ├── docker-spark-*/
│   ├── docker-notebook/
│   └── docker-postgres/
├── data/                   # Shared data volume
├── notebooks/              # JupyterLab notebooks
└── logs/                   # Airflow logs
```

## Airflow Connections Required

### Spark Connection (spark_default)
- Connection Type: Spark
- Host: spark://spark
- Port: 7077

### PostgreSQL Connection (postgres_default)
- Connection Type: Postgres
- Host: postgres
- Schema: airflow
- Login: airflow
- Password: airflow
- Port: 5432

## Development Notes

- The project uses Poetry for Python dependency management (pyproject.toml)
- Python version: 3.9+
- Airflow runs in LocalExecutor mode (single-node)
- Spark cluster shares volumes with Airflow for accessing DAG files and data
- JupyterLab can connect to the Spark cluster for interactive development
- All services share the `data/` directory for file exchange

## Docker Image Naming Convention

Images follow the pattern: `data-etl-{component}`
- data-etl-base
- data-etl-spark-base
- data-etl-spark-master
- data-etl-spark-worker
- data-etl-airflow
- data-etl-notebook
- data-etl-postgres
