"""
###############################################################################
prefs - Access and create preference files for tools.

Getting Started
---------------


###############################################################################
"""
import getpass
import json
import os
import sys
from xml.etree import ElementTree as ET

import blurdev
from blurdev import osystem


def find(name, coreName='', shared=False, index=0):
	""" Follows previous conventions to attempt to find a specific prefs file.

	Args:
		name(str): A full or relative filepath to the prefs file.
		coreName(str): Base of path to look for prefs
		shared(bool): Whether prefs is in a local or networked location
		index(int): Index of prefs file for duplicates

	Returns:
		Prefs: A prefs file or an empty prefs file if none is found.

	"""
	if os.path.exists(name):
		pref = Prefs(name)
	else:
		key = str(name).replace(' ', '-').lower()
		if index > 0:
			key = '%s%s' % (key, index)
		pref = Prefs()
		# look for a default preference file
		filename = os.path.join(pref.path(coreName, shared), '%s.pref' % key)
		pref.load(filename)
	success = False
	return pref

class SmartDict(dict):
	def __getitem__(self, key):
		if key.startswith("_"):
			return
		if not self.get(key):
			newdict = SmartDict()
			self[key] = newdict
			return newdict
		else:
			return super(SmartDict, self).__getitem__(key)

	def __getattr__(self, key):
		if not key.startswith("_"):
			return self[key]

	def __setattr__(self, prop, value):
		self[prop] = value

class Prefs(object):
	def __init__(self, filepath="", data=None):
		self._data = data
		if not self._data:
			self._data = dict()
		if filepath:
			self.load(filepath)
		self.ignore = self.__dict__.keys()
		self.ignore.append('ignore')
		self.setAttrs()

	def __str__(self):
		return json.dumps(
			self.data,
			indent=4,
			separators=(',', ': ')
		)

	def __eq__(self, other):
		return str(self) == str(other)

	def __getattr__(self, prop):
		# Do not attempt to retrieve any private properties
		if prop.startswith("_"):
			return
		if not self._data.get(prop):
			self._data[prop] = SmartDict()
		return self._data[prop]

	def __getitem__(self, key):
		if not self._data.get(key):
			self._data[key] = SmartDict()
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value
		self.setAttrs()

	@property
	def data(self):
		for key, val in self.__dict__.iteritems():
			if key not in self._data.keys() and key not in self.ignore:
				self._data[key] = val
		return self._data

	def initializeXML(self):
		""" Initializes the data from an xml document. """
		# Use the old preference object ot pull the xml data
		oldprefs = ET.parse(self.filepath)
		data = self.extractXMLData(oldprefs)
		return data

	def extractXMLData(self, prefs):
		""" Extracts each element in an xml into a key/value store. """
		# Retrieve the root and store everything under the root
		rootkey =  prefs.getroot().tag
		rootvalue = self.traverse(prefs.getroot())
		# return {rootkey : rootvalue}
		return rootvalue

	def get(self, key, default=None):
		""" Retrieves a value from the key provided.

		Retrieves a valued from the provided key.  Also, can provide a default
		value if the key does not exist in the data store.

		Args:
			key(str) : Key from values wished to retrieve
			default(Object|None) : Default value to provide if no value exists.

		Returns:
			Object : an object retrieved from the key.

		"""
		return self._data.get(key, default)

	def recordProperty(self, prop, value):
		""" **DEPRECATED** A backport for the old prefs to store prefs data.

		Args:
			prop(str) : Key to store
			value(object) : Value to attribute with the key

		Returns:
			None

		Raises:
			None

		"""
		self._data[key] = value

	def restoreProperty(self, key, default):
		""" **DEPRECATED** A backport for the old prefs to retrive prefs data.

		Args:
			key(str) : Element key to retrieve
			default(object) : If key is not present, default value to pass
		"""

	def setAttrs(self):
		""" Store all the key value pairs as properties for the instance.
		"""
		for key, value in self._data.iteritems():
			if not key.startswith("_"):
				setattr(self, key, value)

	def traverse(self, root):
		""" Recursive traverse an xml to retrieve the data.

		Args:
			root(xml.etree.ElementTree.Element) : Root element of xml

		Returns:
			SmartDict object to store

		"""
		data = SmartDict()
		element = root
		# Add all the top level items for that element
		for key, value in root.attrib.iteritems():
			# Attempt to store the evaluation of the xml string
			try:
				# value types, JSON doesn't directly work with this
				if type(eval(value)) == type:
					data[key] = value
				else:
					data[key] = eval(value)
			except (NameError, SyntaxError) as e:
				data[key] = value
		# Recursively traverse through children
		if element.getchildren():
			for child in element.getchildren():
				childkey = child.tag
				data[childkey] = self.traverse(child)
		return data

	def path(self, coreName='', shared=False):
		""" return the path to the application's prefrences folder """
		# use the core
		if (not coreName and blurdev.core):
			coreName = blurdev.core.objectName()
		path = ''
		if shared:
			path = osystem.expandvars(
				os.environ['BDEV_PATH_PREFS_SHARED']
			) % {'username': getpass.getuser()}
		# if not shared or the path does not exist use the non shared path.
		# This is for user accounts who do not
		# get network shared preference locations.
		if not path or not os.path.exists(path):
			path = osystem.expandvars(os.environ['BDEV_PATH_PREFS'])
		return os.path.join(path, 'app_%s' % coreName)

	def save(self, path=""):
		""" Writes the data to file.

		Args:
			path(str) : Path to the file if not already stored.

		Returns:
			None

		"""
		if not path:
			path = self.filepath
		with open(path, 'w') as fh:
			json.dump(
				self.data,
				fh,
				indent=4,
				separators=(',', ': ')
			)

	def load(self, filepath):
		""" Loads the key/value store from a file.

		Args:
			filepath(str) : Path to file to load data.

		Returns:
			None

		Raises:
			IOError: File is not present
			ValueError: File cannot be ingested

		"""
		self.filepath = filepath
		if self.filepath:
			try:
				with open(self.filepath, 'r') as fp:
					self._data = json.load(fp)
			except (IOError, ValueError) as e:
				# Handle if the file is not there
				if type(e) == IOError:
					self._data = {}
					return
				# This may be an xml
				self._data = self.initializeXML()
				self.setAttrs()
