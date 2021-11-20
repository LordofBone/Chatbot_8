sudo apt-get update
sudo apt-get install curl libpq-dev -qq
sudo usermod -aG docker "$USER"
curl -fsSL https://get.docker.com/ | sh