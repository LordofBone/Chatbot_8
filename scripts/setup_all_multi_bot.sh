RCol='\e[0m'
Whi='\e[0;97m'
Red='\e[1;31m'
Gre='\e[1;32m'
Yel='\e[1;33m'
Blu='\e[1;34m'
Pur='\e[1;35m'
Cya='\e[1;36m'
Org='\033[01;38;5;202m'

echo -e "${Whi}<<Configuring Container>>${RCol}"

echo -e "${Red}Updating apt-get & upgrading${RCol}"
apt-get update -qq >/dev/null && apt-get full-upgrade -qq >/dev/null

echo -e "${Org}Installing apt-get packages${RCol}"
apt-get install -qq \
  python3-pip \
  python3-dev \
  libpq-dev \
  git \
  build-essential \
  postgresql-server-dev-13 \
  nano >/dev/null

echo -e "${Yel}Installing pip packages${RCol}"
pip3 install -qq -r /Chatbot_8/requirements.txt

echo -e "${Gre}Cloning smlar from git${RCol}"
git clone --quiet git://sigaev.ru/smlar

echo -e "${Cya}Making & installing smlar${RCol}"
cd smlar || exit
# need to find a way to totally mute make commands - it still throws a warning here
USE_PGXS=1 make --quiet --silent --ignore-errors
USE_PGXS=1 make install --quiet --silent --ignore-errors

echo -e "${Pur}Giving execute permissions to sh files${RCol}\n"
cd /
chmod +x /Chatbot_8/scripts/start_multi_bot.sh /Chatbot_8/scripts/train_multi_bot.sh >/dev/null

echo -e "${Whi}<<Configuring Chatbot 1 & 2 DB & running training on both>>${RCol}"
cd Chatbot_8 || exit
./scripts/train_multi_bot.sh
