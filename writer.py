
from datetime import datetime, timedelta

class Writer(object):

	def __init__(self, filename):
		self.branch_csv = open(filename + "-branch.csv", 'w')
		self.commit_csv = open(filename + "-commit.csv", 'w')
		self.repostats_csv = open(filename + "-repostats.csv", 'w')

	def write_headers(self):
		branchHeader = "id,num commits,branch files,avg branch files pc,commit files,avg commit files pc,branch locs added, branch locs removed,branch locs total,avg branch locs total pc,commit locs added, commit locs removed,commit locs total,avg commit locs total pc,branch hunks,avg branch hunks pc,commit hunks,avg commit hunks pc,num unique authors,num unique committers,commit start time,commit end time,commit time window,author start time, author end time,author time window"
		self.branch_csv.write(branchHeader + '\n')

		commitHeader = "id,files,locs added,locs removed,locs total,hunks,commit time,author time"
		self.commit_csv.write(commitHeader + '\n')

	def write_repo_stats(self, summaryName, statistic):
		self.repostats_csv.write(summaryName + "," + str(statistic) + "\n")

	def write_commit_data(self, node, child, numFiles, numLocsAdded, numLocsRemoved, numHunks, cDate, aDate):
		uniqueID = node + "..." + child

		locsTotal = numLocsAdded + numLocsRemoved

		self.commit_csv.write(uniqueID + ',')
		self.commit_csv.write(str(numFiles) + ',')
		self.commit_csv.write(str(numLocsAdded) + ',')
		self.commit_csv.write(str(numLocsRemoved) + ',')
		self.commit_csv.write(str(locsTotal) + ',')
		self.commit_csv.write(str(numHunks) + ',')
		self.commit_csv.write(str(cDate) + ',')
		self.commit_csv.write(str(aDate) + '\n')


	def write_branch_data(self, node, child, diffstats, numCommits, numUniqueCommitters, numUniqueAuthors, commitStartTime, commitEndTime, authorStartTime, authorEndTime, combinedCommitLocAdded, combinedCommitLocRemoved, combinedCommitHunk, combinedCommitFile):

		uniqueID = node + '...' + child
		numUniqueFiles = str(len(diffstats.keys()))

		branchLocAdded = 0
		branchLocRemoved = 0
		branchHunkTotal = 0
		for key in diffstats.keys():
			branchLocAdded = branchLocAdded + int(diffstats[key][0])
			branchLocRemoved = branchLocRemoved + int(diffstats[key][1])
			branchHunkTotal = branchHunkTotal + int(diffstats[key][2])

		# do some calculations
		branchLocTotal = branchLocAdded + branchLocRemoved
		combinedCommitLoc = combinedCommitLocAdded + combinedCommitLocRemoved
		avgFilesPerCommit = int(numUniqueFiles) / float(numCommits)
		avgCommitFileSizePerCommit = int(combinedCommitFile) / float(numCommits)
		avgBranchLoc = branchLocTotal / float(numCommits)
		avgCommitLoc = combinedCommitLoc / float(numCommits)
		avgBranchHunk = branchHunkTotal / float(numCommits)
		avgCommitHunk = combinedCommitHunk / float(numCommits)

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
		self.branch_csv.write(str(combinedCommitFile) + ',')
		self.branch_csv.write(str(avgCommitFileSizePerCommit) + ',')
		self.branch_csv.write(str(branchLocAdded) + ',')
		self.branch_csv.write(str(branchLocRemoved) + ',')
		self.branch_csv.write(str(branchLocTotal) + ',')
		self.branch_csv.write(str(avgBranchLoc) + ',')
		self.branch_csv.write(str(combinedCommitLocAdded) + ',')
		self.branch_csv.write(str(combinedCommitLocRemoved) + ',')
		self.branch_csv.write(str(combinedCommitLoc) + ',')
		self.branch_csv.write(str(avgCommitLoc) + ',')
		self.branch_csv.write(str(branchHunkTotal) + ',')
		self.branch_csv.write(str(avgBranchHunk) + ',')
		self.branch_csv.write(str(combinedCommitHunk) + ',')
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
		self.repostats_csv.close()

