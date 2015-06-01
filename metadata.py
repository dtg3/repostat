#!/usr/bin/python

class Metadata(object):
	committer    = ""
	author       = ""
	commit_date  = ""
	author_date  = ""
	msg          = ""
	body         = " "

	def __init__(self, c, a, cd, ad, m, b):
		self.committer    = c
		self.author       = a
		self.commit_date  = cd
		self.author_date  = ad
		self.msg          = m

		if b is None:
			self.body = ''
		else:
			self.body = b

	def debug(self):
		print "committer   = " + self.committer
		print "author      = " + self.author
		print "commit_date = " + str(self.commit_date)
		print "author_date = " + str(self.author_date)

		if self.msg is not None:
			print "subject = " + self.msg

		if self.body is not None:
			print "body    = " + self.body

	def fdel(self):
		del self.committer
		del self.author
		del self.commit_date
		del self.author_date
		del self.msg
		del self.body
