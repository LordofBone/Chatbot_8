@echo off
set /p cb="Enter Chatbot name to build: "
docker run --name %cb% -p 5432:5432 -d -it chatbot_db_base
docker cp ../ %cb%:/Chatbot_8
docker exec %cb% bash -c "chmod +x /Chatbot_8/scripts/setup_all_multi_bot.sh ; ./Chatbot_8/scripts/setup_all_multi_bot.sh"
docker stop %cb%
pause