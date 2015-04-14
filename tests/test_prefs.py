import os
import pytest
from prefs import find, Prefs

# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def prefs():
	prefs_path = os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		"foo.prefs"
	)
	return Prefs(prefs_path)

@pytest.fixture
def fromxml():
	xml_path = os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		"xml.prefs",
	)
	return Prefs(xml_path)

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_get_by_properties(prefs):
	assert prefs.foo == "FOO"
	assert prefs.bar == "BAR"
	assert prefs.spam == 1234.0

def test_set_by_properties(prefs):
	prefs.testbyprop = "TESTING"
	assert prefs.testbyprop == "TESTING"

def test_get_by_keys(prefs):
	assert prefs['foo'] == "FOO"
	assert prefs['bar'] == "BAR"
	assert prefs['spam'] == 1234.0

def test_set_by_keys(prefs):
	prefs['testbykey'] = "KEYADDED"
	assert prefs['testbykey'] == "KEYADDED"

def test_find(prefs):
	""" Find function """
	test_path = os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		"foo.prefs"
	)
	found_prefs = find(test_path)
	created_prefs = Prefs(test_path)
	assert created_prefs == found_prefs

def test_creation():
	pass

def test_backwards_compatibility(fromxml):
	assert fromxml.name == "test"
	assert fromxml['geometry']['type'] == "QRect"

def test_save():
	savepath = os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		"save.prefs"
	)
	# Remove any old prefs
	if os.path.exists(savepath):
		os.remove(savepath)
	assert not os.path.exists(savepath)
	prefs = Prefs(savepath)
	prefs.foo = "TEST"
	prefs.save()
	loadedPrefs = Prefs(savepath)
	assert loadedPrefs.foo == "TEST"

def test_save(prefs):
	# Save out the path
	savepath = os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		"saved.prefs"
	)
	if os.path.exists(savepath):
		os.remove(savepath)
	assert not os.path.exists(savepath)
	prefs.save(savepath)
	assert os.path.exists(savepath)
	newprefs = Prefs(savepath)
	assert newprefs.foo == "FOO"

def test_nested_properties():
	test = Prefs()
	test['foo']['bar']['spam'] = 'Hello'
	assert test["foo"]["bar"]["spam"] == "Hello"

if __name__ == "__main__":
	# test_find("")
	pytest.main()
