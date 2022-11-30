@echo off
set /p pgc="Enter PostgreSQL container name: "
set /p pt="Enter PostgreSQL port (default=5432): "
docker run --name %pgc% -p 5432:5432 -d -p %pt%:5432 chatbot_db_base
docker cp ../scripts/setup_postgresql.sh %pgc%:/
docker exec %pgc% bash -c "chmod +x setup_postgresql.sh ; ./setup_postgresql.sh"
docker stop %pgc%
pause