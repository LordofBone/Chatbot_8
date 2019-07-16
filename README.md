# Chatbot_8

To run this you will need to install:

pip install fuzzywuzzy

sudo apt-get install mongodb && sudo service mongodb start

python -m pip install pymongo==3.4.0


And then run the main file:

python bot_8.py


To add in training data put in a file with the text called 'learning.txt' then run:

python bot_8_trainer.py

It should skip most non-text lines and split conversation text away from name assignments, eg. "Tim: Hello" will only read "Hello".
