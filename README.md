# docker-data-etl

This project is a data etl flow with airflow and spark:

A simple data etl flow extract news by web crawler, use jieba to cut the words, load the data to postgres

- architecture
```mermaid
flowchart

    user
    user
    user
    
    master("master")
    worker1("worker1")
    worker2("worler2")
    worker3("worler3")
    
    db[("Postgres")]
    notebook("jupyerlab")
    
    user

    subgraph spark-cluster["spark-cluster(standalone)"]
    
        direction TB
        master --> worker1 
        master --> worker2 
        master --> worker3

    end
    
    subgraph airflow ["Airflow"]
    
        
    
    end
    
    db <--> airflow
    
    user --> airflow
    user --> notebook
    
    notebook -..-> spark-cluster
    airflow--> spark-cluster
    
```

* build image
`bash build.sh {image_name}`

* get started with docker compose
`docker-compose up -d`



## Note
  
  This project is modified from https://github.com/pappas999/chainlink-hardhat-box

