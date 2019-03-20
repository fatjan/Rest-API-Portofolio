#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/Rest-API-Portofolio &&
sudo git pull

sudo source ~/.profile
sudo echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin
sudo docker stop ecommerce_container1007
sudo docker rm ecommerce_container1007
sudo docker rmi fatjan/ecommerce
sudo docker run -d --name ecommerce_container1007 -p 5001:5001 fatjan/ecommerce:latest
