#!/bin/bash
docker build -t flask-base ../base_flask
docker build -t node-base ../base_node
docker build -t tornado-base ../base_tornado
docker build -t notification-service ./notification_service
docker build -t frontend ./frontend
docker build -t calculation-service ./calc_service
docker build -t backend ./backend