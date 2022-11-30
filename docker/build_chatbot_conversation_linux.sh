docker run --name "$1" -p 5432:5432 -d -it chatbot_db_base
docker cp ../ "$1":/Chatbot_8
docker exec "$1" bash -c "chmod +x /Chatbot_8/scripts/setup_all_multi_bot.sh ; ./Chatbot_8/scripts/setup_all_multi_bot.sh"
docker stop "$1"
