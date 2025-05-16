# Copyright (c) 2025, mbwcloud.com and Contributors
# See license.txt

# import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class UnitTestATS_Recruitment_Process(UnitTestCase):
	"""
	Unit tests for ATS_Recruitment_Process.
	Use this class for testing individual functions and methods.
	"""

	pass


class IntegrationTestATS_Recruitment_Process(IntegrationTestCase):
	"""
	Integration tests for ATS_Recruitment_Process.
	Use this class for testing interactions between multiple components.
	"""

	pass
