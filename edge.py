
from metadata import Metadata

# edges used for squishing linear branches
class Edge(object):
	_parent = ""
	_weight = 1
	_nparent = "" # for cases when _parent is NULL
	committers = set()
	authors = set()
	files = set()
	locByBranch = 0
	locByCommitSum = 0
	hunkByBranch = 0
	hunkByCommitSum = 0
	commitStartTime = ""
	commitEndTime = ""
	authorStartTime = ""
	authorEndTime = ""

	def __init__(self, p, weight, np):
		self._parent = p
		self._weight = weight
		self._nparent = np
		self.committers = set()
		self.authors = set()
		
	def fdel(self):
		del self._parent
		del self._weight
		del self._nparent
		del self.committers
		del self.authors
		del self.files
		del self.locByBranch
		del self.locByCommitSum
		del self.hunkByBranch
		del self.hunkByCommitSum
		del self.commitStartTime
		del self.commitEndTime
		del self.authorStartTime
		del self.authorEndTime

