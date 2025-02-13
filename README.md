# WoTtrader
WoTtrader is a trading service for the WoT that extends the W3C recommendation of discovery service by increasing the functionality of the API and by allowing the integration of a set of capabilities that gives the discovery service the ability to adapt to the evolution of IoT systems. The discovery service has a set of capabilities that extend the discovery process; these capabilities are (a) a recommender system, (b) proactive discovery, (c) federated discovery, and (d) query expansion. WoTtrader supports syntactic, semantic and natural language search, and query delegation using the federation capability. Furthermore for semantic queries, third-party discovery services can benefit from this capability and delegate their queries through the WoTtrader network. 


# Docker quick start for one single node
---

```
version: '3.8'

services:

  wottrader1:
    image: acgtic211/wottrader:1.0.0
    ports:
      - "3021:3000"
    depends_on:
      - mongodb1
      - jena-fuseki1
    environment:
      - MONGODB_URI_DEVELOPMENT=mongodb://wot_admin:pw1234@mongodb1:27017/
      - MONGODB_DATABASE=node-database
      - FUSEKI_URI_DEVELOPMENT=http://jena-fuseki1:3030/wottrader
      - FUSEKI_USERNAME=admin
      - FUSEKI_PASSWORD=pw123
      - WEB_APP_PORT=3000
    command: >
      sh -c "
      /wait-for-it.sh mongodb1:27017 -- 
      /wait-for-it.sh jena-fuseki1:3030 -- 
      npm start"
    networks:
      - wottrader

  mongodb1:
    image: bitnami/mongodb:4.4
    ports:
      - "27121:27017"
    environment:
      - MONGODB_ROOT_PASSWORD=pw1234
      - MONGODB_USERNAME=wot_admin
      - MONGODB_PASSWORD=pw1234
      - MONGODB_DATABASE=node-database
    volumes:
      - mongodb_data1:/data/db
      - ./init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
    networks:
      - wottrader

  jena-fuseki1:
    image: stain/jena-fuseki
    ports:
      - "3121:3030"
    environment:
      - ADMIN_PASSWORD=pw123
      - TDB=2
    volumes:
      - "fuseki_data1:/fuseki"
      - "./fuseki-config.ttl:/staging/fuseki-config.ttl"
    command: >
      sh -c "
      cp /staging/fuseki-config.ttl /fuseki/config.ttl &&
      /jena-fuseki/fuseki-server"
    networks:
      - wottrader

  central-server:
    image: acgtic211/central-server:1.0.0
    ports:
      - "7999:7999"
    networks:
      - wottrader

  web-discovery:
    image: acgtic211/web-discovery:1.0.0
    ports:
      - "80:80"
    networks:
      - wottrader

  triplestore:
    image: acimmino/auroral-fuseky:latest
    environment:
     ADMIN_PASSWORD: pw123
    volumes:
    - triplestore:/fuseki
    ports:
      - '3030:3030'
    networks:
      - wottrader
  wothive:
    image: acimmino/wot-hive:latest
    # volumes:
    # - ./configuration.json:/usr/src/wothive/configuration.json
    ports:
      - '9000:9000'
    networks:
      - wottrader

  TinyIoT:
    image: ghcr.io/tinyiot/thing-directory
    ports:
      - '8081:8081'
    networks:
      - wottrader

networks:
  wottrader:

volumes:
  mongodb_data1:
  fuseki_data1:
  triplestore:
```

The `docker-compose.yml` file must be in a folder with the files `fuseki-config.ttl` and `init-mongo.js`.

Run the docker command

```
docker-compose up -d
```

The API documentation is available in an OpenAPI service at the url `http://localhost:3021/docs/`.

# Docker experimental scenario

For deploying an experimental scenario with 8 nodes and 2 third-party nodes use the docker-compose file of the repository.

The dataset used in the experimental scenario is available in the `dataset` folder. It includes all the devices and associated node information for each of the nodes in the scenario. To populate the directories run the python script `poblateDirectories.py`. Each data is stored with a delay of 5 seconds to avoid overloading the system. In the case of WoTHive, for syntactic search it may fail to load the context of all devices. In case of failure, reduce the number of available devices in WoTHive.

Each node contains a script to not deploy the node until the databases are deployed. In case of failure, restart the affected nodes to connect to the database.

![Experimentation scenario map.](images/ScenaryMap.png)
