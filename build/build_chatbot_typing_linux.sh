docker run --name "$1" -e POSTGRES_PASSWORD="$2" -d -it postgres:13
docker cp ../ "$1":/Chatbot_8
docker exec "$1" bash -c "chmod +x /Chatbot_8/scripts/setup_all.sh ; ./Chatbot_8/scripts/setup_all.sh ; echo -n ' -t -b $1' >> /Chatbot_8/scripts/start.sh"
docker stop "$1"
