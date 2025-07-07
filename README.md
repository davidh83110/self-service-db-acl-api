# Self-Service DB Anti-Corruption Layer API
[![CI](https://github.com/davidh83110/self-service-db-acl-api/actions/workflows/ci-build.yaml/badge.svg?branch=main)](https://github.com/davidh83110/self-service-db-acl-api/actions/workflows/ci-build.yaml)
[![Deploy](https://github.com/davidh83110/self-service-db-acl-api/actions/workflows/cd.yaml/badge.svg?branch=main)](https://github.com/davidh83110/self-service-db-acl-api/actions/workflows/cd.yaml)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

## Overview

### This is a Flask RESTful API with Postgres database running locally.
- [http://localhost:3000](http://localhost:3000) - Main endpoint showing available routes
- [http://localhost:3000/health](http://localhost:3000/health) - Health check endpoint
- [http://localhost:3000/update](http://localhost:3000/update) - Configuration update endpoint (POST)

![Flask Status](img/flask_status.png)

### We also launch a registry in the local Kubernetes cluster
🐳 Docker Registry 
```bash
curl -X GET http://127.0.0.1:30500/v2/_catalog
curl -X GET http://127.0.0.1:30500/v2/postgres/tags/list  
```

### CI/CD (Github Actions)
We host a self-hosted Github Runner for CI/CD. When the changes are committed, the workflows [ci-build.yaml](.github/workflows/ci-build.yaml) and [cd.yaml](.github/workflows/cd.yaml) will be triggered to build and push the images to local registry, then update the deployments if needed.


## How to Run
This page will only focus on the Flask application. 
If you need any information about `Helm` or running in `Kubernetes`, 
please visit [deploy/README.md](deploy/README.md).

### Quick Run
#### Docker Compose for launching without Kubernetes
```bash
docker-compose up --build -d
```

#### Kind and Helm Chart
```bash
cd ./deploy
sh ./startup.sh
```
- For more information, please visit [deploy/README.md](deploy/README.md).

### Prerequisites
- Python >= 3.10
- Pipenv
- Docker 
- Redis Server

### Setup Environment
- Install Pipenv 
  ```bash
  python -m pip install --upgrade pip
  pip install pipenv --no-cache-dir
  ```
- Install Dependencies
  ```bash
  pipenv install --system --deploy --ignore-pipfile
  ```

  
### Start Flask Application
#### In Gunicorn without Docker
```bash
gunicorn --bind 0.0.0.0:3000 \
            --access-logfile flask-app-gunicorn.log \
            --error-logfile flask-app-gunicorn-error.log \
            --log-level debug \
            wsgi:app
```

#### In Gunicorn with Docker
- Build Docker Image
  ```bash
   export APP_VERSION=0.0.1
   docker build --build-arg APP_VERSION=$APP_VERSION --no-cache -t flask-app .
  ```
- Run Docker Container
  ```bash
  docker run -p 3000:3000 -it flask-app
  ```


### Check Result
After the application is started, you can always visit the pages on browser:
[http://localhost:3000](http://localhost:3000)

### Update Configuration
You can dynamically update the API configuration using the `/update` endpoint:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "api_endpoint": "/categories",
  "query": "SELECT id, name, description FROM categories;",
  "columns": {
    "id": "category_id",
    "name": "category_name",
    "description": "category_description"
  }
}' http://localhost:3000/update
```

This will add or update an API endpoint configuration without requiring a server restart.


## Development
### Run under Pipenv Shell  
```bash
pipenv install --deploy
pipenv shell
python3 main.py
```
or 
```bash
pipenv install --deploy
pipenv run python3 main.py
```

### Install PyPI packages with Pipenv
```bash
pipenv install flask ...
pipenv update
```

### Run Unittest
```bash
pipenv shell
pytest
```


## CI/CD 
I use `Github Actions` to implement a simple CI/CD pipeline, 
which includes `unittest`, `SAST evaluation`, `docker build and push`, and `helm upgrade`.
- Please visit [ci-build.yaml](.github/workflows/ci-build.yaml) and [cd.yaml](.github/workflows/cd.yaml).
- SAST tool - [bandit](https://github.com/PyCQA/bandit)
- We could possibly optimize the pipeline to be faster and comment some messages on the Pull Request, but I just ignore those things since it is a demo only.

### The CI Pipeline
Build and Push Docker Images of Flask and Postgres to local registry

### The CD Pipeline
- Update ConfigMap if needed
- Upgrade Helm charts if needed
> We should improve the authentication. Now I'm just using a Service Account for this Runner.

![Kubernetes Status](img/kube_status.png)

## Versioning
![Registry List](img/registry_list.png)

I use a [VERSION](VERSION) file to control the Application version, which will be the `APP_VERSION` when we build the Docker Image.
But in real environment, I think we can do it with `tags triggering`, `auto increment`, or integrate with `Jira`/`Github Project`. 

For Postgres versioning, the image tag will always be the `Git Commit ID`.
