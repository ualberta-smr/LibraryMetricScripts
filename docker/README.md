# How to run the website using Docker

This is a simple way to get a local librarycomparison web development server set up.

You'll need to have Docker and Docker Compose installed.

- You first need to set up some of the configuration parameters in the file `Config.json`:
	- Change the value of `TOKEN` to your own GitHub generated token. ([How to create Github TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#github-token))
	- Change the value of `SO_TOKEN` to your stack exchange key. ([How to create StackOverflow TOKEN](https://github.com/ualberta-smr/LibraryMetricScripts/wiki/Creating-access-tokens#stackoverflow-token))
- Updates the Database Host and Port in `settings.py`.
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',        
        'NAME': 'libcomp',
        'USER': 'root',
        'HOST': 'db',
        'PORT' : 3306,
     	'PASSWORD': 'enter pwd',
    }
}
```

- You can update the `MAXSIZE` to 100 in `Config.json` for testing purpose.

## Creating the image

1. Builds/Rebuilds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build --no-cache
```

2. Starts the containers
**Run metric script:**
```
docker-compose run metric-script
```
-   `createmetrics`: Create the Metrics
-   `updatemetrics`: Update the Metrics (password for root user is `enter pwd`)
**Open librarycomparisons website command shell:**
```
docker exec -it librarycomparisons_web sh ./start.sh
```
-   `start`: Starts the Django server. The librarycomparison web will run in the `8000` port by default. 
-   `migrate`: Runs Django migrations
-   `make`: Runs Django makemigrations
-   `createsuperuser`: Runs Django createsuperuser

To access the website, use http://127.0.0.1:8000/comparelibraries/

3. Stops containers and removes containers, networks, volumes, and images created by up

```
docker-compose down
```
