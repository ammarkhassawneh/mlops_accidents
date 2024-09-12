#!/bin/bash

python3 docker/generate_env_keys.py

docker-compose -f docker/docker-compose.yml up

