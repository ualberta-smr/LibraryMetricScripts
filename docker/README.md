Temp notes for updating ReadMe:

- had to run the down with -v to delete data
- followed exact instructions... but noticed that you have to run createmetrics from inside the script in docker-compose step (seems in parallel with leaving the other things running). Need to clarify that in instructions
- Had a problem with the SO key because my key was on old version of API. Had to do it for API V2.0
- Next step is to check: if I exit metrics container, is data still saved in DB? Can I import the DB dump in DB and have it reflect in website? Can I trigger update in the container from localhost? Right now, the release data is taking time to be calculated.
- Remove note about MAXSIZE since it's not used anymore
- Add note that for testing, reduce num of libs in the lib file

# How to calculate metrics & run visualization website using docker

This is a simple way to run the metrics and also get a local website setup to view the metrics (similar to [https://smr.cs.ualberta.ca/comparelibraries/](https://smr.cs.ualberta.ca/comparelibraries/)

You'll need to have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

- After cloning this repo, you first need to set up some of the configuration parameters in the file `scripts/Config.json`:
	- Change the value of `TOKEN` to your own GitHub generated token. ([How to create Github TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#github-token)).
	- Change the value of `SO_TOKEN` to your stack exchange key. ([How to create StackOverflow TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#stackoverflow-token)). Please make sure to create a token for v2.0 of the API.
    - Change `"OUTPUT_PATH"` to  `"../home/scripts/"`.

- You can update the `MAXSIZE` to 100 in `Config.json` for testing purpose.

## Creating the image
### 1. Builds/Rebuilds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build --no-cache
```

### 2. Starts the containers

**Starts the containers && Starts the website**
```
docker-compose up
```
To access the website, use http://127.0.0.1:8000/comparelibraries/

**Run metric script:**
The above step will have the website running, but right now, there is no data in the DB yet to be displayed. To calculate the metrics, run:

```
docker-compose run metric-script
```

This will open an interactive shell into the container and you can then invoke `createmetrics` to calculate the Metrics:

```
root@e7c767ab1a70:/main# createmetrics
```

**(Optional) Open librarycomparisons website command shell:**
```
docker-compose run --service-ports web
```
-   `start`: Starts the Django server. The librarycomparison web will run in the `8000` port by default. 
-   `migrate`: Runs Django migrations
-   `make`: Runs Django makemigrations
-   `createsuperuser`: Runs Django createsuperuser

To access the website, use http://127.0.0.1:8000/comparelibraries/

### 3. Stops containers and removes containers, networks, volumes, and images created by up

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
