#!/bin/bash

health_check() {
  MAX_RETRIES=60
  RETRY_COUNT=0
  until curl -L -s -o /dev/null -w "%{http_code}" $1 | grep -q "200"; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Services are not ready after $MAX_RETRIES retries."
        exit 1
    fi
    echo "Waiting for services to start... (Attempting: $RETRY_COUNT)"
    sleep 3
  done

  echo "Server is up and running."
  curl -L $1
}


# Check kind
kind version
if [[ $? -eq 0 ]]; then
  echo "kind found."
else
  echo "kind not found, please try to install by \`brew install kind\` (MacOS)."
  exit 1
fi;

## Create Kind Cluster
kind create cluster --config ./kind-conf.yaml -n kind-flask

## Install Ingress-Nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -f ./ingress-nginx-values.yaml
sleep 3

## Install Local Registry
kubectl apply -f ./registry.yaml
sleep 3
health_check "http://localhost:30500/v2/_catalog"

## Build and Push Images
docker-compose -f ../docker-compose.yaml build
docker-compose -f ../docker-compose.yaml push

## Deploy PostgresDB
kubectl create configmap mydb-init --from-file=../databases/init.sql

helm upgrade -i postgres bitnami/postgresql -f postgres-values.yaml
sleep 3

## Apply CM/secret
kubectl create configmap flask-config --from-file=../config.yaml
kubectl apply -f ./flask-secrets.yaml

## Deploy Flask
sleep 15 # wait for redis and Nginx are ready
helm upgrade -i flask-app ./charts -f ./flask-app-values.yaml

## Check results
helm list
kubectl get pod
health_check "http://localhost:3000/health"
