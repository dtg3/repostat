
from edge import Edge
from datetime import datetime

class Writer(object):

	def __init__(self, filename):
		self.branch_csv = open(filename + "-branch.csv", 'w')
		self.commit_csv = open(filename + "-commit.csv", 'w')


	def write_headers(self):
		branchHeader = "id,num commits,num unique files,avg files pc,branch locs, avg branch locs pc,commit locs,avg commit locs pc,branch hunks,avg branch hunks pc,commit hunks,avg commit hunks pc,num unique authors,num unique committers,commit start time,commit end time,commit time window,author start time, author end time,author time window"
		self.branch_csv.write(branchHeader + '\n')

	def write_commit_data(self, node, child, commitStats):
		uniqueID = node + "..." + child

	def write_branch_data(self, node, child, diffstats, cacheInfo, combinedCommitLoc, combinedCommitHunk):

		uniqueID = node + '-' + child
		numUniqueFiles = str(len(diffstats.keys()))

		branchLocTotal = 0
		commitLocTotal = combinedCommitLoc
		branchHunkTotal = 0
		commitHunkTotal = combinedCommitHunk
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
		commitStartTime = cacheInfo.commitStartTime
		commitEndTime = cacheInfo.commitEndTime
		authorStartTime = cacheInfo.authorStartTime
		authorEndTime = cacheInfo.authorEndTime


		# do some calculations
		avgFilesPerCommit = int(numUniqueFiles) / float(numCommits)
		avgBranchLoc = branchLocTotal / float(numCommits)
		avgCommitLoc = commitLocTotal / float(numCommits)
		avgBranchHunk = branchHunkTotal / float(numCommits)
		avgCommitHunk = commitHunkTotal / float(numCommits)

		# get the times as strings without the local time addition (e.g., " + 0400")
		commitStartTimeNoLocale = commitStartTime[:19]
		commitEndTimeNoLocale = commitEndTime[:19]
		authorStartTimeNoLocale = authorStartTime[:19]
		authorEndTimeNoLocale = authorEndTime[:19]

		# save time strings as datetime objects
		cStart = datetime.strptime(commitStartTimeNoLocale, "%Y-%m-%d %H:%M:%S")
		cEnd = datetime.strptime(commitEndTimeNoLocale, "%Y-%m-%d %H:%M:%S")
		aStart = datetime.strptime(authorStartTimeNoLocale, "%Y-%m-%d %H:%M:%S")
		aEnd = datetime.strptime(authorEndTimeNoLocale, "%Y-%m-%d %H:%M:%S")

		# calculate differences
		commitTimeWindow = cEnd - cStart
		authorTimeWindow = aEnd - aStart

		# TODO: only use hours and hour decimals in the time windows

		# write out row
		self.branch_csv.write(uniqueID + ',')
		self.branch_csv.write(str(numCommits) + ',')
		self.branch_csv.write(numUniqueFiles + ',')
		self.branch_csv.write(str(avgFilesPerCommit) + ',')
		self.branch_csv.write(str(branchLocTotal) + ',')
		self.branch_csv.write(str(avgBranchLoc) + ',')
		self.branch_csv.write(str(commitLocTotal) + ',')
		self.branch_csv.write(str(avgCommitLoc) + ',')
		self.branch_csv.write(str(branchHunkTotal) + ',')
		self.branch_csv.write(str(avgBranchHunk) + ',')
		self.branch_csv.write(str(commitHunkTotal) + ',')
		self.branch_csv.write(str(avgCommitHunk) + ',')
		self.branch_csv.write(str(numUniqueAuthors) + ',')
		self.branch_csv.write(str(numUniqueCommitters) + ',')
		self.branch_csv.write(commitStartTimeNoLocale + ',')
		self.branch_csv.write(commitEndTimeNoLocale + ',')
		self.branch_csv.write(str(commitTimeWindow).replace(',','') + ',')
		self.branch_csv.write(authorStartTimeNoLocale + ',')
		self.branch_csv.write(authorEndTimeNoLocale + ',')
		self.branch_csv.write(str(authorTimeWindow).replace(',',''))
		self.branch_csv.write('\n')

	def close(self):
		self.branch_csv.close()
		self.commit_csv.close()

	def fdel(self):
		del committer
		del author
		del commit_date
		del author_date




