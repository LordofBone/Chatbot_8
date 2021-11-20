@echo off
set /p cb="Enter Chatbot name to build: "
FOR /F "tokens=1-2 USEBACKQ" %%A IN (`type ..\config\postgresql_config.yaml`) DO (SET password=%%B)
docker run --name %cb% -e POSTGRES_PASSWORD=%password% -d -it postgres:13
docker cp ../ %cb%:/Chatbot_8
docker exec %cb% bash -c "chmod +x /Chatbot_8/scripts/setup_all_multi_bot.sh ; ./Chatbot_8/scripts/setup_all_multi_bot.sh"
docker stop %cb%
pause