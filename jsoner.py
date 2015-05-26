#!/usr/bin/python
import json, pprint

class Jsoner(object):

	def __init__(self, filename):
		self.file = open(filename + ".json", 'w')
		self.json = {}
		self.json['stats'] = {}
		self.json['stats']['octopi'] = 0
		self.json['segments'] = []

	def addSegment(self):
		self.json['segments'].append({})
		index = len(self.json['segments']) - 1
		self.json['segments'][index]['commits'] = {}
		self.json['segments'][index]['euclidean'] = self.formDiffStats(0, 0, 0, [])

	def addCommitToLastSegment(self, sha, commitObject):
		self.json['segments'][len(self.json['segments'])-1]['commits'][sha] = commitObject

	def addEuclideanToLastSegment(self, euclideanObject):
		self.json['segments'][len(self.json['segments'])-1]['euclidean'] = euclideanObject

	def formCommitStats(self, parents, children, committer, author, ctime, atime, message, body, origin, cstats):
		return {
			"parents" : parents,
			"children" : children,
			"committer" : committer,
			"author" : author,
			"ctime" : str(ctime),
			"atime" : str(atime),
			"subject" : message,
			"body" : body,
			"origin" : origin,
			"cstats" : cstats
		}

	def formDiffStats(self, aloc, dloc, hunks, files):
		return { "aloc" : aloc, "dloc" : dloc, "hunks" : hunks, "files" : list(files)}

	def finish(self):
		json.dump(self.json, self.file, indent=4)
		self.file.close()

