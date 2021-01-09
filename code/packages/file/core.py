import os
import zipfile
import tarfile
import pandas
import string
from shutil import copyfile
import sys

class Core():
	
	def __init__(self, path, writeHeader = True):
		parts = path.split('/')
		self.path = path
		self.fileName = parts[len(parts) - 1]

		parts = path.split('.')
		self.extension = parts[len(parts) - 1]

		self.file = None
		self.lines = None
		self.lineNumber = 0
		self.writeHeader = writeHeader
		return


	def getFileName(self):
		return self.fileName


	def exists(self):
		return os.path.exists(self.path)


	def open(self, mode = "w"):
		self.file = open(self.path, mode, encoding="utf-8")
		return


	def close(self):
		self.file.close()
		return


	def remove(self):
		if self.exists():
			os.unlink(self.path)
		return


	def load(self, mode = 'r'):
		if self.extension == 'csv':
			self.file = pandas.read_csv(self.path, sep=',', encoding='latin1', quotechar='"')
			self.lines = self.file.values
			return

		self.open(mode)
		self.lines = self.file.read()
		self.close()
		
		return


	def write(self, content, mode = None):
		if not mode:
			if self.exists():
				mode = 'a+'
			else:
				mode = 'w+'
		self.open(mode)
		if self.extension == 'csv':
			dataFrame = pandas.DataFrame(content, [0])
			dataFrame.to_csv(self.file, header = self.writeHeader, index = False)
			self.writeHeader = False
		else:
			self.file.write(content)

		self.close()
		return


	def read(self, mode = 'r'):
		if(not self.lines):
			self.load(mode)
		return self.lines


	def readLine(self):
		if(not self.lines):
			self.load()
		line = self.lines[self.lineNumber]
		self.lineNumber = self.lineNumber + 1
		return line


	def zip(self, filePaths):
		self.file = zipfile.ZipFile(self.path, "w")
		if hasattr(filePaths, "__len__"):
			for filePath in filePaths:
				self.file.write(filePath)
		else:
			self.file.write(filePaths)
		self.file.close()


	def isPdfFile(self):
		return self.extension == 'pdf'


	def isCsvFile(self):
		return self.extension == 'csv'


	def isZipFile(self):
		return zipfile.is_zipfile(self.path)


	def isTarFile(self):
		return tarfile.is_tarfile(self.path)


	def unzip(self):
		self.file = zipfile.ZipFile(self.path)
		for fileName in self.file.namelist():
			self.file.read(fileName)
		self.file.close()
		return


	def untar(self):
		destinationPath = self.path.replace(self.fileName, '')
		tar = tarfile.open(self.path)
		tar.extractall(destinationPath)
		tar.close()
		return

	@staticmethod
	def copy(sourcePath, destinationPath):
		copyfile(sourcePath, destinationPath)
		return


	@staticmethod
	def join(*args):
		return os.path.join(*args)


