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

inputWords = ("hello")
globalReply = ("hello")
botAccuracy = 0.725
botAccuracyLower = 0.1

learnClass = b.talkLoop(client, db, responses, allwords, inputWords, globalReply, botAccuracy, botAccuracyLower)
learnClass.updateDB(inputWords, globalReply)
inputWords = (learnClass.replyTumbler())
learnClass.updateDB(inputWords, globalReply)
globalReply = (learnClass.replyTumbler())

try:
	if sys.argv[1] == ("fresh"):
		print("Clearing DB")
		d.delDB()
except:
	print("Existing DB training")

f = open("learning.txt", "r")

for x in f:
	inputWords = x
	
	if not re.search('[a-zA-Z]', inputWords):
		continue
		
	print("Sentence: " + inputWords)
	print("Reply: " + globalReply)
	
	learnClass.updateDB(inputWords, globalReply)

	globalReply = x
