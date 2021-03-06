# docker-data-etl

This project is a data etl flow with airflow and spark:

A lightweight data etl flow extract news by web crawler, use jieba to cut the words, load the data to postgres

### architecture
```mermaid
flowchart

    user("Data Enginner")
    
    
    master("master")
    worker1("worker1")
    worker2("worler2")
    worker3("worler3")
    
    db[("Postgres")]
    notebook("Jupyerlab")
    
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

### build image

- use `build.sh`

`bash build.sh {image_name}`

- `Makefile`

``make build-all``


* Get started with docker compose

```docker-compose up -d```


### Service

- [airflow](http://0.0.0.0:/8282)
- [spark](http://0.0.0.0:8080)
- [jupyterlab](http://0.0.0.0:8888)


### Airflow connection

- set spark connection

![](https://i.imgur.com/0mVRf18.png)

- postgres connection

![](https://i.imgur.com/VyQf2dU.png)


### ETL

![](https://i.imgur.com/qRnngUg.png)

- extract: web crawler
- transformation: wordcount using spark
- load: spark write data to postgres




## Reference


https://medium.com/data-arena/building-a-spark-and-airflow-development-environment-with-docker-f0b9b625edd8

https://github.com/cluster-apps-on-docker/spark-standalone-cluster-on-docker

https://hub.docker.com/r/bitnami/spark

https://github.com/puckel/docker-airflow

