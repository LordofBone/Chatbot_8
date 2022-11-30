docker run --name "$1" -d -it chatbot_db_base
docker cp ../ "$1":/Chatbot_8
docker exec "$1" bash -c "chmod +x /Chatbot_8/scripts/setup_all.sh ; ./Chatbot_8/scripts/setup_all.sh ; echo -n ' -t -b $1' >> /Chatbot_8/scripts/start.sh"
docker stop "$1"
