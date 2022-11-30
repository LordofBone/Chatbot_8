sudo apt-get update
sudo apt-get install curl libpq-dev -qq
curl -fsSL https://get.docker.com/ | sh
sudo usermod -aG docker "$USER"