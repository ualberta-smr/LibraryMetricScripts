# How to run the website using Docker

This is a simple way to get a local librarycomparison web development server set up.

You'll need to have Docker and Docker Compose installed.

- You first need to set up some of the configuration parameters in the file `Config.json`:
	- Change the value of `TOKEN` to your own GitHub generated token. ([How to create Github TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#github-token))
	- Change the value of `SO_TOKEN` to your stack exchange key. ([How to create StackOverflow TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#stackoverflow-token))
    - Change `"OUTPUT_PATH"` to  `"../home/scripts/"`.

- You can update the `MAXSIZE` to 100 in `Config.json` for testing purpose.

## Creating the image
### 1. Builds/Rebuilds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build --no-cache
```

### 2. Starts the containers
**Starts the containers && Start the server**
```
docker-compose up
```
**Run metric script:**
```
docker-compose run metric-script
```
-   `createmetrics`: Create the Metrics
**(Optional) Open librarycomparisons website command shell:**
```
docker-compose run --service-ports web
```
-   `start`: Starts the Django server. The librarycomparison web will run in the `8000` port by default. 
-   `migrate`: Runs Django migrations
-   `make`: Runs Django makemigrations
-   `createsuperuser`: Runs Django createsuperuser

To access the website, use http://127.0.0.1:8000/comparelibraries/

### ### 3. Stops containers and removes containers, networks, volumes, and images created by up

```
docker-compose down
```
Remove volume: `docker-compose down -v`. Warning: this will permanently delete the contents in the db_data volume, wiping out any previous database you had there

### 4. Setup Metric Table if you create the docker volumn for the first time
```
docker exec  librarymetricscripts_db_1 /bin/sh -c  'mysql -uroot -p"mypwd"  libcomp  < docker-entrypoint-initdb.d/metric-setup.sql'
```

## Accessing docker container mysql databases
1. docker exec -it MyContainer mysql -uroot -pMyPassword
eg: `docker exec -it librarymetricscripts_db_1 mysql -uroot -p"mypwd"`
2. Show MySQL Databases: `show databases;`
```
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| libcomp            |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
```
3. Show MySQL Tables: 
```
use libcomp;
show tables;
```
4. Show Table's schema
```
describe libcomp.Metric;
```
5. Show the values of Metric table
```
select * from libcomp.Metric;
```
