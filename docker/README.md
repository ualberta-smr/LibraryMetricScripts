## Docker Local Development Setup

This is a simple way to get a local librarycomparison web development server set up.

You'll need to have Docker and Docker Compose installed.
You'll need to clone [librarycomparisonswebsite](https://github.com/ualberta-smr/librarycomparisonswebsite) repo and [LibraryMetricScripts](https://github.com/ualberta-smr/LibraryMetricScripts) repo from Github in your local folder.

## Creating the image

1. Builds the image (not start the containers) in the docker-compose.yml file:

```
docker-compose build
```

2. Starts the containers

```
docker-compose up
```

3. Stops containers and removes containers, networks, volumes, and images created by up

```
docker-compose down
```

## Reference
* [docker-compose](https://docs.docker.com/compose/reference/overview/)
