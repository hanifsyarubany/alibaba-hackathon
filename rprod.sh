#!/bin/bash

# Define the usage function
usage() {
  echo "Usage: $0 {service|service+mongo|service+mongo+redis|all}"
  exit 1
}

# Check if the script has been run with an argument
if [ $# -eq 0 ]; then
  usage
fi

# Define the action based on the argument
case "$1" in
  service)
    echo "Starting FastAPI service only..."
    docker compose down
    docker compose up -d --build --remove-orphans fastapi_app
    ;;
  
  service+mongo)
    echo "Starting FastAPI service and MongoDB..."
    docker compose down
    docker compose up -d --build --remove-orphans mongodb
    docker compose up -d --build --remove-orphans fastapi_app
    ;;
  
  service+mongo+redis)
    echo "Starting FastAPI service, MongoDB, and Redis..."
    docker compose down
    docker compose up -d --build --remove-orphans mongodb redis
    docker compose up -d --build --remove-orphans fastapi_app
    ;;
  
  all)
    echo "Starting all services..."
    docker compose down
    docker compose up -d --build --remove-orphans mongodb redis rabbitmq vectordb
    docker compose up -d --build --remove-orphans fastapi_app
    ;;
  
  *)
    usage
    ;;
esac
