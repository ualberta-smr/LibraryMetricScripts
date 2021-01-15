## Docker Local Development Setup

This is a simple way to get a local librarycomparison web development server set up.

You'll need to have Docker and Docker Compose installed.
You'll need to clone [librarycomparisonswebsite](https://github.com/ualberta-smr/librarycomparisonswebsite) repo and [LibraryMetricScripts](https://github.com/ualberta-smr/LibraryMetricScripts) repo from Github in your local folder.

## Creating the image

1. Builds/Rebuilds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build --no-cache
```

2. Starts the containers

```
docker-compose up -d && docker exec -it librarycomparison sh ./LibraryMetricScripts/docker/start.sh
```

You can now connect to the server at `127.0.0.1:8000`.

You can run some commands definded in `docker/start.sh` file:
-   `start`: Starts the Django server. The librarycomparison web will run in the `8000` port by default. 
-   `migrate`: Runs Django migrations
-   `make`: Runs Django makemigrations
-   `createsuperuser`: Runs Django createsuperuser
-   `updatemetrics`: Update the Metrics

3. Stops containers and removes containers, networks, volumes, and images created by up

```
docker-compose down
```

## Hint
* If you see `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on '127.0.0.1' (61)")`, because you are not starting the mysql.  You can run ` /etc/init.d/mysql start`.
* If you see `django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'localhost' (using password: YES)")`, You need to make changes in librarycomparison settings.py. Provide `USER` and `PASSWORD` for your database.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'libcomp',
        'USER': 'root',
        'PASSWORD': 'my_root_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
If you forget your root password for MySQL (MySQL 8), you can reset your password on mysql console:
```
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
```
* If you hit `MySQLdb._exceptions.OperationalError: (1049, "Unknown database 'libcomp'")` error, you can run `create database libcomp;` in MySQL (you need to install MySQL frist).


## Reference
* [docker-compose](https://docs.docker.com/compose/reference/overview/)
