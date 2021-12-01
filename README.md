### Setup

###### Pre-requisites

You can read more about how the Chatbot works here: https://www.hackster.io/314reactor/chatbot-2022-edition-633823 
https://www.electromaker.io/project/view/chatbot-2022-edition

Ensure you have Python 3.9 installed (this is what I have been using for it so far).

Before doing any of the below you will need to set a password for the PostgreSQL database, this can be done by going
into the 'config' folder and accessing 'postgresql_config.yaml' and adding/changing the password; or you can leave it
at the default. 
This will be used in the construction and login of PostgreSQL container databases.

The windows .cmd files will pick the password up from the YAML, but you will need to manually change it in the inputs
for the .sh files, for example: ./build_chatbot_linux.sh *container name *postgres password *postgres port

You will need Docker installed, for linux you can run the script under /build 'install_docker_linux.sh'

On Linux it is handy to have a GUI for Docker as well so run 'portainer_build_linux.sh' and 'portainer_run_linux.sh' 
and then go to localhost:9000 in a browser - as there isn't currently an official Docker UI for Linux yet.

For Windows just go here and download/install:
https://docs.docker.com/desktop/windows/install/

###### _Recommended_ - Entire Chatbot as a Docker container

Drop training files into the '/data/training' folder before building (see 'Training the bot' below).

Set a password for the PostgreSQL DB under '/config/postgresql_config.yaml'

Go into the 'build' folder in this repo and run 'build_chatbot_windows.cmd' or 'build_chatbot_typing_windows.cmd'

Then give the bot a name.

(.sh files available for Linux + Linux on Pi, keep note that the .sh files require the container names, password and 
port put in as parameters with the command).

You can also run 'build_chatbot_conversation_windows.cmd' or .sh (ensuring there are training .txt files under
'/data/training_2' as well as '/data/training') this will configure a container and train 2 different bot databases.
This is to see how bots with different training configurations will interact with each other.

###### Local PostgreSQL installation

Follow the instructions here: https://www.2ndquadrant.com/en/blog/pginstaller-install-postgresql/

Make sure that the password is set and the same as the password in '/config/postgresql_config.yaml'

You will then need to ensure the requirements are installed:

`pip install -r requirements.txt`

This also uses something called 'smlar' which needs to be installed with PostgreSQL:

`git clone git://sigaev.ru/smlar`

`cd smlar`

`USE_PGXS=1 make -s`

`USE_PGXS=1 make install -s`

I don't know if there is a Windows installation for smlar so if you are running on Windows I would recommend a Docker
based installation.

###### Docker PostgreSQL installation

I would recommend going into the 'build' folder and running 'build_postgresql_container_windows.cmd' or .sh and entering a name
and port number (recommended to just use the default: 5432); these scripts will handle it all for you.

However, if you wish to construct the container manually see below:

**Manual:**

Make sure the DB password is set in '/config/postgresql_config.yaml' and that the password set is used in the command
below.

`docker run --name postgresdb -e POSTGRES_PASSWORD=<password> -d -p 5432:5432 postgres`

Again, you will then need to ensure the requirements are installed:

`pip install -r requirements.txt`

As above, you will need to install 'smlr' you can exec into the PostgreSQL container and run:

`git clone git://sigaev.ru/smlar`

`cd smlar`

`USE_PGXS=1 make -s`

`USE_PGXS=1 make install -s`

### Training the bot

If you are running the bot code outside a container, but with a Docker container for the DB don't forget to set up a 
python venv (https://docs.python-guide.org/dev/virtualenvs/) and install the requirements:

`pip install -r requirements.txt`

Drop training txt files into the '/data/training' folder, these must be formatted as such:

**example.txt:**

_Hello_

_Hi_

_How are you_

Where each line is a reply, the bot can deal with blank lines and also split names from the text like so:

_Me: Hello_

_You: Hi_

_Me: How are you_

It will split these lines by ':' and return the reply only; this makes it easier to paste in things like movie scripts.

You can then run 'bot_8_trainer.py -f' if running a local PostgreSQL or a PostgreSQL in a container.

The '-f' switch there is for a fresh DB which is required for a first time run and will also completely erase any 
existing database.

If you are running a bot within a container it will take in whatever is in the training folder and train automatically
while creating the container.

You can have multiple txt files within the training folder; it will process them all.

As mentioned above there is a second training folder: '/data/training_2', this is for training a second bot for
conversations - both bots can be trained by running 'bot_8_trainer.py -f -m' (-f for fresh DB and -m for multi-bot)

### Running the bot

###### Running the bot as a container

Run 'run_chatbot.cmd' and type the name of the built chatbot.

For a two bot conversation container that has been built you can run 'run_chatbot_conversation.cmd' and then type the name
of the container. You will then see the two bot personas talk to each other. By default this will be set to 'slow' mode;
where there is a one-second delay added between the bots replies, so you can easily see what they are saying (you may
notice it runs slower anyway depending on the size of the dataset).

(.sh files for Linux and Linux on Pi, keep note that the .sh files require the container names, password and 
port put in as parameters with the command).

###### Running the bot on either a local or containerised PostgreSQL DB

Ensure that PostgreSQL is running, either from the local installation or the container as above.

Run 'bot_8.py' and it should connect to the running local instance or the running container of PostgreSQL.

Run 'bot_conversation.py' to initiate a conversation between two bots (provided above training has been run for both).
You can also add a '-f' switch to make it run without an additional delay (it may still run slower depending on the size
of the training data).

### How it works

The chatbot essentially takes in words from the human user and adds them to the prior text.

For instance if you say "_hello_" to it and it replies "_how are you_" and you say "_not bad, thanks_" it will remember
that as a response to "_how are you_" - so the next time a user inputs something similar to that, for example:
"_how are ya_" it will fuzzy match that, find "_how are you_" as the closest match and then pick a reply assigned to
that. In this case: "_not bad, thanks_".

If the bot has no responses it will pick a random sentence or generate a random sentence from words it knows.

The more you interact with the bot the more it will be able to talk coherently - if it is trained on a decent sized
training set that has a good number of decent conversations and replies in it; it will be even better.

The bot can also keep track of different conversations between different people - if you put in your name as "Joe" and
then talk with it, then type _"change_name"_ and type in "Pete", it will keep the last reply from "Joe" and move onto a
new conversation with "Pete".

You can then get back to the "Joe" conversation by typing _"change_name"_ again and typing "Joe". This functionality was
implemented because I want to use this chatbot in a robot sometime and have that robot potentially talk to multiple
people.

You will have also noticed there are two version of the bot to build - the "typing" and "non-typing" version; the typing
version will try and emulate the behaviour of another person at a keyboard.

It has a random wait before it starts to 'type' on top of the time it takes the DB to search and other processes to
happen. Then it starts printing _'Bot is typing...'_ for each word with an estimated typing speed of 2.7KPS (keystrokes
per second). With a 5% chance that between words it will stop typing for a few seconds.

So the longer the sentence the more time it will take to 'type' - I added in this feature to try to give the illusion of
another person; personally I find it quite effective, but it may require tweaking.

Finally, you can exit the bot by stopping the container, exiting Python or by typing "bye" the bot will give a final
response, then exit. If it is a containerised version then it will also stop the container.

### Using the bot as a part of another program

If you want to integrate the bot into another system, such as a robot - you can pull down the repo into the folder of
the project you are working on, then in the folder you can run 'pip install -e Bot8' with the current project python
environment activated.

Running the '-e' flag puts it into editable mode which means you can easily access the '/config/postgresql_config.yaml'
and add in a password for the database; As well as being able to edit the bot overall.

Within the Bot8/build folder there is a build_postgresql_container.cmd you can use to quickly build a DB container.
Ensure this is running also before proceeding.

Within the Bot8 folder you can add training files into '/data/training' then training can be run:

`from Bot8.bot_8_trainer import bot_trainer`

`bot_trainer()`

Then simply import the bot and then initialise the BotLoop class.

For example:

`from Bot8.bot_8 import BotLoop`

`chat = BotLoop()`

`reply = chat.conversation("how are you")`

`print(reply)`

You can also import 'person_manager' and use it to create different names of people to talk to the bot. You could use
this functionality with an import of the bot to have multiple conversations running simultaneously; by simply passing in
the different names into the 'person_manager' function, using 'get_person_list' to get the dict of initialised classes
back and then use that to run different conversations using the names as keys.

For example:

`from Bot8.bot_8 import BotLoop, person_manager, get_person_list`

`print(person_manager("Joe"))`

`print(person_manager("Bob"))`

`names = get_person_list()`

`reply_1 = names["Joe"].conversation("hello there")`

`reply_2 = names["Bob"].conversation("hows it going")`

`print(reply_1)`

`print(reply_2)`

There is a way to install Bot8 with pip without putting it into editable mode (similar to how most pip packages are
installed) with 'pip install Bot8/' with the current project python environment activated. With this the Bot8 folder
does not need to be present within your project folder - _however_ this results in the YAML config not being present as
well as the 'training' folders not being accessible.

I have not yet found a way to allow the modules to be able to access folders in the root folder (for 'training' &
'config') when installed this way - the 'training' and 'config' folders will be under 'site-packages' in this way and as
such will not be easy to edit and add training files.

If anyone knows a way around this please let me know.

### Misc.

I don't have a Dockerfile setup for this - I am using the scripts above as it is an easier way to get the PostgreSQL DB
up and running by initialising the PostgreSQL image via the run command.

This command sets up the DB and everything with the entrypoint for you, then I copy in the bootstrapping files and run 
those to configure the bot and run training etc.

I have tried to get this working within a Dockerfile but couldn't get it to configure and run the DB after installation,
if someone can make a Dockerfile that does what the build scripts do, please let me know.

I would recommend containerising the bot, this way you can have multiple personas of the bot, each with their own DB.

You can of course have multiple PostgreSQL containers with different personas and run the bot code locally.