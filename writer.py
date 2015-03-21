
from edge import Edge

class Writer(object):

	def __init__(self, filename):
		self.branch_csv = open(filename + "-branch.csv", 'w')
		self.commit_csv = open(filename + "-commit.csv", 'w')


	def write_headers(self):
		branchHeader = "id,num unique files,branch loc total,commit loc sum,branch hunk total,commit loc sum,num unique authors,num unique committers,commit start time,commit end time,author start time, author end time,num commits"
		self.branch_csv.write(branchHeader + '\n')

	def write_data(self, node, child, diffstats, cacheInfo):

		uniqueID = node + '-' + child
		numUniqueFiles = str(len(diffstats.keys()))

		branchLocTotal = 0
		commitLocTotal = 0
		branchHunkTotal = 0
		commitHunkTotal = 0
		numUniqueAuthors = 0
		numUniqueCommitters = 0
		commitStartTime = ""
		commitEndTime = ""
		authorStartTime = ""
		authorEndTime = ""
		numCommits = 0

		for key in diffstats.keys():
			branchLocTotal = branchLocTotal + int(diffstats[key][0])   # lines added
			branchLocTotal = branchLocTotal + int(diffstats[key][1])   # lines removed
			branchHunkTotal = branchHunkTotal + int(diffstats[key][2]) # hunks

		numCommits = cacheInfo._weight
		numUniqueCommitters = len(cacheInfo.committers)
		numUniqueAuthors = len(cacheInfo.authors)

		print "diffstats keys is: " + str(len(diffstats.keys())) + ", num files from cache is: " + str(len(cacheInfo.files))

		commitStartTime = cacheInfo.commitStartTime
		commitEndTime = cacheInfo.commitEndTime
		authorStartTime = cacheInfo.authorStartTime
		authorEndTime = cacheInfo.authorEndTime




		#_parent = ""
		#_weight = 1
		#####_nparent = "" # for cases when _parent is NULL
		#committers = set()
		#authors = set()
		#####files = set()
		locByBranch = 0
		locByCommitSum = 0
		hunkByBranch = 0
		hunkByCommitSum = 0
		#commitStartTime = ""
		#commitEndTime = ""
		#authorStartTime = ""
		#authorEndTime = ""


		self.branch_csv.write(uniqueID + ',')
		self.branch_csv.write(numUniqueFiles + ',')
		self.branch_csv.write(str(branchLocTotal) + ',')
		self.branch_csv.write(str(commitLocTotal) + ',') # TODO
		self.branch_csv.write(str(branchHunkTotal) + ',')
		self.branch_csv.write(str(commitHunkTotal) + ',') # TODO
		self.branch_csv.write(str(numUniqueAuthors) + ',') # TODO
		self.branch_csv.write(str(numUniqueCommitters) + ',') # TODO
		self.branch_csv.write(commitStartTime + ',') # TODO
		self.branch_csv.write(commitEndTime + ',') # TODO
		self.branch_csv.write(authorStartTime + ',') # TODO
		self.branch_csv.write(authorEndTime + ',') # TODO
		self.branch_csv.write(str(numCommits)) # TODO
		self.branch_csv.write('\n')

	def close(self):
		self.branch_csv.close()
		self.commit_csv.close()

	def fdel(self):
		del committer
		del author
		del commit_date
		del author_date




