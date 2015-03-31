

import json
import os
import sys

class Prefs(object):

	def __init__(self, path="", data={}):
		self.path = path
		self._data = data
		if self.path:
			with open(self.path, 'r') as fp:
				self._data = json.load(fp)
		self.ignore = self.__dict__.keys()
		self.ignore.append('ignore')

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
