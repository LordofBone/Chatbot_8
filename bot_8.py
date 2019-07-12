import sys
import random
import pymongo
import datetime
import sys
import time
import numpy
import random
from pymongo import MongoClient
from pprint import pprint
from colors import *
from difflib import SequenceMatcher

client = MongoClient('localhost', 27017)
db = client.words_database
responses = db.responses
allwords = db.allwords

inputWords = ("hello")
globalReply = ("hello")
botAccuracy = 0.725
botAccuracyLower = 0.45

class talkLoop(object):

	def __init__(self, client, db, responses, allwords, inputwords, globalReply, botAccuracy, botAccuracyLower):
		self.client = client
		self.db = db
		self.responses = responses
		self.allwords = allwords
		self.inputwords = inputwords
		self.globalReply = globalReply
		self.botAccuracy = botAccuracy
		self.botAccuracyLower = botAccuracyLower
		
	def similar(self, a, b):
		return SequenceMatcher(None, a, b).ratio()
		
	def get_random_doc(self):
		count = self.allwords.count()
		return self.allwords.find()[random.randrange(count)]
		
	def sentenceGen(self):
		result = ""
		length = random.randint(1, 10)
	
		for i in range(length):
			cursor = self.get_random_doc()
			for x, y in cursor.items():
				if x == "word":
					cWord = (y)
					result += cWord
					result += ' '
					del cursor
	
		return result
	
	def dbSearch(self, searchIn):
		cursor = self.responses.find_one({"whatbotsaid": searchIn})
		for x, y in cursor.items():
			if x == 'humanReply':
				chosenReply = (random.choice(y))
		del cursor
		return chosenReply
		
	def mongoFuzzyMatch(self, inputString, searchZone, termZone, setting):
		compareList = {}
		for cursor in searchZone.find():
			for x, y in cursor.items():				
				if x == termZone:
					compareNo = self.similar(inputString, y)
					if setting == ('off'):
						compareList[y] = compareNo
					elif setting == ('med'):
						if compareNo > self.botAccuracyLower:
							compareList[y] = compareNo
					elif setting == ('on'):
						if compareNo > self.botAccuracy:
							compareList[y] = compareNo
		if compareList == {}:
			compareChosen = 'none_match'		
		else:
			compareChosen = max(compareList.iterkeys(), key=(lambda key: compareList[key]))
		del cursor
		return compareChosen

	def replyTumbler(self):
		searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'on')
		if searchSaid == ('none_match'):
			searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'med')
			if searchSaid == ('none_match'):
				if random.randrange(100) <= 60:
					print("sentence")
					searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'off')
					chosenReply = self.dbSearch(searchSaid)			
				else:	
					chosenReply = self.sentenceGen()
					print("guess")
			else:
				chosenReply = self.dbSearch(searchSaid)
		else:		
			chosenReply = self.dbSearch(searchSaid)
		del searchSaid
		return (chosenReply)

	def updateDB(self, wordsIn, bResponse):
		self.wordsIn = wordsIn
		self.bResponse = bResponse
		cursor = self.responses.find_one({"whatbotsaid": self.bResponse})

		if cursor is None:
			postR = {"whatbotsaid": self.bResponse, "humanReply": [self.wordsIn]}
			self.responses.insert_one(postR).inserted_id
			del cursor
		else:
			self.responses.update({"whatbotsaid": self.bResponse}, {'$addToSet':{"humanReply": self.wordsIn}}, upsert=True)
			del cursor
		wordsInDB = self.wordsIn.split(' ')
		for word in wordsInDB:
			cursor = self.allwords.find_one({"word": word})
			if cursor is None:
				postW = {"word": word}
				self.allwords.insert_one(postW).inserted_id
			else:
				pass
			del cursor

if __name__ == "__main__":

	talkClass = talkLoop(client, db, responses, allwords, inputWords, globalReply, botAccuracy, botAccuracyLower)
	talkClass.updateDB(inputWords, globalReply)
	inputWords = (talkClass.replyTumbler())
	talkClass.updateDB(inputWords, globalReply)
	globalReply = (talkClass.replyTumbler())
	sys.stdout.write(BLUE)
	print (globalReply)
	sys.stdout.write(RESET)

	while True:
		sys.stdout.write(GREEN)
		inputWords = raw_input('You:	')
		sys.stdout.write(RESET)
		if inputWords == (""):
			continue
		talkClass.updateDB(inputWords, globalReply)
		globalReply = (talkClass.replyTumbler())
		sys.stdout.write(BLUE)
		print(globalReply)
		sys.stdout.write(RESET)
