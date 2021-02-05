## Docker Local Development Setup

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
- Updates hostname from `127.0.0.1` to `db` in updatemetrics.sh
`mysqldump --no-tablespaces --no-create-info --complete-insert --skip-triggers  -h db --user=root -p libcomp Domain Library Issue Metric LibraryRelease MetricsEntry Chart ProjectType TeamType PluginUser PluginUser_groups PluginUser_projects PluginUser_teams PluginFeedback WebsiteFeedback > $file_name`

- You can update the `MAXSIZE` to 100 in `Config.json` for testing purpose.

## Creating the image

1. Builds/Rebuilds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build --no-cache
```

2. Starts the containers (open both metric-script and web)
**Open metric script command shell:**
```
docker-compose run metric-script
```
-   `updatemetrics`: Update the Metrics (password for root user is `enter pwd`)

**Open librarycomparisons website command shell (Another Tab):**
```
docker-compose up -d && docker exec -it librarycomparisons_web sh ./start.sh
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


## Reference
* [docker-compose](https://docs.docker.com/compose/reference/overview/)
