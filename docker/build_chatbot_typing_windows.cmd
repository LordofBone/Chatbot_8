@echo off
set /p cb="Enter Chatbot name to build: "
docker run --name %cb% -d -it chatbot_db_base
docker cp ../ %cb%:/Chatbot_8
docker exec %cb% bash -c "chmod +x /Chatbot_8/scripts/setup_all.sh ; ./Chatbot_8/scripts/setup_all.sh ; echo -n ' -t -b %cb%' >> /Chatbot_8/scripts/start.sh"
docker stop %cb%
pause