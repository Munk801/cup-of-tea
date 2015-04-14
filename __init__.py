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


def find(name, reload=False, coreName='', shared=False, index=0):
	"""
	Finds a preference for the with the inputed name.  If a pref already
	exists within the cache, then the cached pref is returned; otherwise,
	it is loaded from the blurdev preference location.

	:param name: the name of the preference to retrieve
	:type name: str
	:param reload: reloads the cached item
	:type reload: bool
	:param coreName: specify a specific core name to save with.
	:type coreName: str
	:param shared: save to the network path not localy. Defaults to False
	:type shared: bool
	:param index: if > 0 append to the end of name. used to make multiple
				  instances of the same prefs file. If zero it will not
				  append anything for backwards compatibility. Defaults to 0
	:type index: int
	:rtype: :class:`Preference`

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

class Prefs(object):
	def __init__(self, filepath="", data={}):
		self._data = data
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

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value

	@property
	def data(self):
		for key, val in self.__dict__.iteritems():
			if key not in self._data.keys() and key not in self.ignore:
				self._data[key] = val
		return self._data

 	def initializeXML(self):
		# Use the old preference object ot pull the xml data
		oldprefs = ET.parse(self.filepath)
		data = self.extractXMLData(oldprefs)
		return data

	def extractXMLData(self, prefs):
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
		"""
		self._data[key] = value

	def setAttrs(self):
		for key, value in self._data.iteritems():
			setattr(self, key, value)

	def traverse(self, root):
		data = {}
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
			path = osystem.expandvars(os.environ['BDEV_PATH_PREFS_SHARED']) % {'username': getpass.getuser()}
		# if not shared or the path does not exist use the non shared path. This is for user accounts who do not
		# get network shared preference locations.
		if not path or not os.path.exists(path):
			path = osystem.expandvars(os.environ['BDEV_PATH_PREFS'])
		return os.path.join(path, 'app_%s' % coreName)

	def save(self, path=""):
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
