

import json
import os
import sys

from blurdev import prefs as bp

class Prefs(object):

	def __init__(self, path="", data={}):
		self.path = path
		self._data = data
		if self.path:
			try:
				with open(self.path, 'r') as fp:
					self._data = json.load(fp)
			except ValueError as e:
				# This may be an xml
				self._data = self.initializeXML()
		self.ignore = self.__dict__.keys()
		self.ignore.append('ignore')

	def initializeXML(self):
		# Use the old preference object ot pull the xml data
		oldprefs = bp.Preference()
		oldprefs.load(self.path)
		data = self.extractXMLData(oldprefs)
		return data

	def extractXMLData(self, prefs):
		# Retrieve the root and store everything under the root
		rootkey =  prefs.root().name()
		rootvalue = self.traverse(prefs.root())
		return {rootkey : rootvalue}

	def traverse(self, root):
		data = {}
		element = root
		# Add all the top level items for that element
		for key, value in root.attributeDict().iteritems():
			# Attempt to store the evaluation of the xml string
			try:
				data[key] = eval(value)
			except NameError as e:
				data[key] = value
		# Recursively traverse through children
		if element.children():
			for child in element.children():
				childkey = child.name()
				data[childkey] = self.traverse(child)
		return data

	def __str__(self):
		return json.dumps(
			self.data,
			sort_keys=True,
			indent=4,
			separators=(',', ': ')
		)

	def __getitem__(self, key):
		return self.data[key]

	def __setitem__(self, key, value):
		self._data[key] = value

	@property
	def data(self):
		for key, val in self.__dict__.iteritems():
			if key not in self._data.keys() and key not in self.ignore:
				self._data[key] = val
		return self._data

	def save(self):
		with open(self.path, 'w') as fh:
			json.dump(
				self.data,
				fh,
				sort_keys=True,
				indent=4,
				separators=(',', ': ')
			)

	def load(self):
		pass
