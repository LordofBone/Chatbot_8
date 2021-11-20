@echo off
set /p cb="Enter Chatbot conversation name to start: "
docker start %cb%
docker exec -it %cb% bash -c "./Chatbot_8/scripts/start_multi_bot.sh"
docker stop %cb%
pause