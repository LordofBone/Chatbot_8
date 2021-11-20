@echo off
set /p pgc="Enter PostgreSQL container name: "
set /p pt="Enter PostgreSQL port (default=5432): "
FOR /F "tokens=1-2 USEBACKQ" %%A IN (`type ..\config\postgresql_config.yaml`) DO (SET password=%%B)
docker run --name %pgc% -e POSTGRES_PASSWORD=%password% -d -p %pt%:5432 postgres:13
docker cp ../scripts/setup_postgresql.sh %pgc%:/
docker exec %pgc% bash -c "chmod +x setup_postgresql.sh ; ./setup_postgresql.sh"
docker stop %pgc%
pause