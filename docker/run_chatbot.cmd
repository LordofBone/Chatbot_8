@echo off
set /p cb="Enter Chatbot name to start: "
docker start %cb%
docker exec -it %cb% bash -c "./Chatbot_8/scripts/start.sh"
docker stop %cb%
pause