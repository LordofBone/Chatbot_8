docker stop portainer
docker rm portainer
docker pull portainer/portainer
docker run -d -p 8000:8000 -p 9000:9000 --name portainer -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer