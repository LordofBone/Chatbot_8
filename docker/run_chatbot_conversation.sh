docker start "$1"
docker exec -it "$1" bash -c "./Chatbot_8/scripts/start_multi_bot.sh"
docker stop "$1"
