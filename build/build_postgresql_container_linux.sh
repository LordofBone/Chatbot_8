docker run --name "$1" -e POSTGRES_PASSWORD="$2" -d -p "$3":5432 -v /var/run/postgresql:/var/run/postgresql postgres:13
docker cp ../scripts/setup_postgresql.sh "$1":/
docker exec "$1" bash -c "chmod +x setup_postgresql.sh ; ./setup_postgresql.sh"
docker stop "$1"