docker run --name "$1" -p 5432:5432 -d -v /var/run/postgresql:/var/run/postgresql chatbot_db_base
docker cp ../scripts/setup_postgresql.sh "$1":/
docker exec "$1" bash -c "chmod +x setup_postgresql.sh ; ./setup_postgresql.sh"
docker stop "$1"