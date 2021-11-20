docker start "$1"
docker exec -it "$1" bash -c "./Chatbot_8/scripts/start.sh"
docker stop "$1"
