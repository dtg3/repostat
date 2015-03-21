
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
		del commitStartTime
		del commitEndTime
		del authorStartTime
		del authorEndTime

