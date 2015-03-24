
from edge import Edge
from datetime import datetime, timedelta

class Writer(object):

	def __init__(self, filename):
		self.branch_csv = open(filename + "-branch.csv", 'w')
		self.commit_csv = open(filename + "-commit.csv", 'w')

	def write_headers(self):
		branchHeader = "id,num commits,branch files,avg branch files pc,commit files,avg commit files pc,branch locs, avg branch locs pc,commit locs,avg commit locs pc,branch hunks,avg branch hunks pc,commit hunks,avg commit hunks pc,num unique authors,num unique committers,commit start time,commit end time,commit time window,author start time, author end time,author time window"
		self.branch_csv.write(branchHeader + '\n')

		commitHeader = "id,files,locs,hunks,commit time,author time"
		self.commit_csv.write(commitHeader + '\n')

	def write_commit_data(self, node, child, numFiles, numLocs, numHunks, metadata):
		uniqueID = node + "..." + child
		files = numFiles
		locs = numLocs
		hunks = numHunks

		cDate = metadata.commit_date
		aDate = metadata.author_date

		self.commit_csv.write(uniqueID + ',')
		self.commit_csv.write(str(files) + ',')
		self.commit_csv.write(str(locs) + ',')
		self.commit_csv.write(str(hunks) + ',')
		self.commit_csv.write(str(cDate) + ',')
		self.commit_csv.write(str(aDate) + '\n')


	def write_branch_data(self, node, child, diffstats, cacheInfo, combinedCommitLoc, combinedCommitHunk, combinedCommitFile):

		uniqueID = node + '...' + child
		numUniqueFiles = str(len(diffstats.keys()))
		combinedCommitFileSize = str(len(combinedCommitFile))


		branchLocTotal = 0
		commitLocTotal = combinedCommitLoc
		branchHunkTotal = 0
		commitHunkTotal = combinedCommitHunk
		numUniqueAuthors = 0
		numUniqueCommitters = 0
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
		avgCommitFileSizePerCommit = int(combinedCommitFileSize) / float(numCommits)
		avgBranchLoc = branchLocTotal / float(numCommits)
		avgCommitLoc = commitLocTotal / float(numCommits)
		avgBranchHunk = branchHunkTotal / float(numCommits)
		avgCommitHunk = commitHunkTotal / float(numCommits)

		# save time strings as datetime objects
		cStart = commitStartTime
		cEnd = commitEndTime
		aStart = authorStartTime
		aEnd = authorEndTime

		# calculate differences
		commitTimeWindow = cEnd - cStart
		cHours, cSecs = divmod(commitTimeWindow.total_seconds(), 3600)
		commitTimeWindowStr = str(cHours + cSecs/3600)

		authorTimeWindow = aEnd - aStart
		aHours, aSecs = divmod(authorTimeWindow.total_seconds(), 3600)
		authorTimeWindowStr = str(aHours + aSecs/3600)

		# write out row
		self.branch_csv.write(uniqueID + ',')
		self.branch_csv.write(str(numCommits) + ',')
		self.branch_csv.write(numUniqueFiles + ',')
		self.branch_csv.write(str(avgFilesPerCommit) + ',')
		self.branch_csv.write(combinedCommitFileSize + ',')
		self.branch_csv.write(str(avgCommitFileSizePerCommit) + ',')
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
		self.branch_csv.write(str(cStart) + ',')
		self.branch_csv.write(str(cEnd) + ',')
		self.branch_csv.write(commitTimeWindowStr + ',')
		self.branch_csv.write(str(aStart) + ',')
		self.branch_csv.write(str(aEnd) + ',')
		self.branch_csv.write(authorTimeWindowStr)
		self.branch_csv.write('\n')

	def close(self):
		self.branch_csv.close()
		self.commit_csv.close()

