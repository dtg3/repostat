#!/usr/bin/python

class Metadata(object):
	committer    = ""
	author       = ""
	commit_date  = ""
	author_date  = ""
	signature    = ""

	def __init__(self, c, a, cd, ad, s):
		self.committer    = c
		self.author       = a
		self.commit_date  = cd
		self.author_date  = ad
		self.signature    = s


	def fdel(self):
		del committer
		del author
		del commit_date
		del author_date
		del signature
