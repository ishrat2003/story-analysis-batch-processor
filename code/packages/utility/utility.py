import math
import hashlib
import json
from file.core import Core as File
import os
import re
import urllib

class Utility():

	""" return the list with duplicate elements removed """
	@staticmethod
	def unique(a):
		return list(set(a))

	""" return the intersection of two lists """
	@staticmethod
	def intersect(a, b):
		return list(set(a) & set(b))

	""" return the union of two lists """
	@staticmethod
	def union(a, b):
		return list(set(a) | set(b))

	@staticmethod
	def diff(a, b):
		return (set(a) - set(b))

	@staticmethod
	def getStopWords():
		path = File.join(os.path.abspath(__file__ + "/../../../resources/"), "nltkData/corpora/stopwords/english")
		file = File(path)
		stopWords = re.split('[\n]', file.read())
		path = File.join(os.path.abspath(__file__ + "/../../../resources/"), 'customStopWords.txt')
		file = File(path)
		customStopWords = re.split('[\n]', file.read())
		return Utility.union(stopWords, customStopWords)

	@staticmethod
	def getPositiveWords():
		path = File.join(os.path.abspath(__file__ + "/../../../resources/"), 'positive.txt')
		file = File(path)
		stopWords = re.split('[\n]', file.read())
		return stopWords

	@staticmethod
	def getNegativeWords():
		path = File.join(os.path.abspath(__file__ + "/../../../resources/"), 'negative.txt')
		file = File(path)
		stopWords = re.split('[\n]', file.read())
		return stopWords

	@staticmethod
	def getDesignations():
		path = File.join(os.path.abspath(__file__ + "/../../../resources/"), 'designation.txt')
		file = File(path)
		designations = re.split('[\n]', file.read())
		return designations

	@staticmethod
	def implode(terms, divider = ','):
		return divider.join(s for s in terms)

	@staticmethod
	def utlencode(params):
		return urllib.parse.urlencode(params)

	@staticmethod
	def getAsciiSum(words):
		words = Utility.unique(words)
		wordsString = ''.join(words)
		asciiSum = 0
		for char in wordsString:
			asciiSum += ord(char)
		
		return asciiSum

	@staticmethod
	def debug(value):
		#print('---------------------------------------------------------------------------------------------')
		print(value)
		print('---------------------------------------------------------------------------------------------')
		return

		



