import sys
import re
import time
import pymongo
from pymongo import MongoClient
import bot_8 as b
import deleteDB as d

client = MongoClient('localhost', 27017)
db = client.words_database
responses = db.responses
allwords = db.allwords

botAccuracy = 0.725
botAccuracyLower = 0.1

name = ("--trainer--")
inputWords = ("hello")

try:
	if sys.argv[1] == ("-fresh"):
		print("Clearing DB")
		d.delDB()
except:
	print("Existing DB training")

b.conversation(inputWords, name)

f = open("learning.txt", "r")

for x in f:
	if not re.search('[a-zA-Z]', x):
		continue

	if x[0] == ("(") or x[0] == ("-") or x[0] == ("*"):
		continue
		
	print(x)

	b.conversation(x, name)

f.close()