#!/usr/bin/python

class Metadata(object):
	committer    = ""
	author       = ""
	commit_date  = ""
	author_date  = ""

	def __init__(self, c, a, cd, ad):
		self.committer    = c
		self.author       = a
		self.commit_date  = cd
		self.author_date  = ad

	def fdel(self):
		del committer
		del author
		del commit_date
		del author_date
