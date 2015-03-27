#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell
import dotter
import sys
from edge import Edge
from writer import Writer
from collections import deque
from datetime import datetime, timedelta, MAXYEAR, MINYEAR
from multiprocessing import Pool, Process, Queue

def init_graph(outputFile):
	graph = open(outputFile, "wb")
	graph.write('graph TD;\n')
	return graph

def end_graph(graph):
	graph.close()

# write to dot graph
def gwrite(graph, child, parent, weight):
	if not parent:
		graph.write('\tNULL-->' + child + ';\n')
	elif weight == 1:
		graph.write('\t' + parent + '-->' + child + ';\n')
	elif weight > 1:
		graph.write('\t' + parent + '-->' + '|' + str(weight) + '| ' + child + ';\n')

def write_csv(diffstats, csvfile):
	if args.csv:
		for key in diffstat.keys():
			csvfile.write(node + ',' + child + ',' + key)

			for item in diffstat[key]:
				csvfile.write(',' + item)
			csvfile.write('\n')


# going bottom (first commit ever) up (most recent)
def is_branch(sha):
	return len(dp[sha]) > 1 # parent has more than one child

def is_merge(sha):
	return len(dc[sha]) > 1 # child has more than one parent

def is_baren(sha):
	return len(dp[sha]) < 1 # has no parents

def is_orphan(sha):
	# todo: we /assume/ it's the first commit, but really it's just a commit
	# with no parents. there can be multiple commits like this in a repo. need
	# a better method of detection
	return sha == NULL    # first commit

def is_linear(sha):
	return len(dp[sha]) == 1 and len(dc[sha]) == 1 # has one parent and one child

def apply_gitshell(commitdiffstat):

	nextParent = commitdiffstat[1]
	lastChild = commitdiffstat[2]

	commitdiffstatp = gitshell.diff(args.repository, nextParent, lastChild)
	commitdiffstat[0] = commitdiffstatp

	return commitdiffstat


def debug_what_am_i(sha):
	if is_branch(sha):
		print sha + " is branch!"
	if is_merge(sha):
		print sha + " is merge!"
	if is_orphan(sha):
		print sha + " is orphan!"
	if is_baren(sha):
		print sha + " is bare!"
	if is_linear(sha):
		print sha + " is linear!"

# main
parser = argparse.ArgumentParser()

parser.add_argument('repository')
parser.add_argument('-s','--svg', type=str)
parser.add_argument('-g','--graph', type=str)
parser.add_argument('-c','--csv', type=str)
parser.add_argument('--branch-diff', type=bool)
parser.add_argument('--branch-sum', type=bool)
parser.add_argument('--no-branch', type=bool)

args = parser.parse_args()

if args.graph:
	graph = init_graph(args.graph) # dot graph

if args.csv:
	w = Writer(args.csv)
	w.write_headers()

# first traversal for mapping parent/child relationship to build up a tree
NULL, dp, dc, dm = gitshell.build_commit_dicts(args.repository)

branch_units = [] # array of branch segments, which are also arrays of commits SHAS.
visited = set()   # all commits that have been visited

# traverse graph to store up branch segments, starting with the null commit
stack = [NULL]
queue = deque([])
while stack:
	# current node - don't want to remove it til we find all branch segments starting at it
	node = stack[0] # peek
	children = dp[node]

	for x in xrange(0,len(children)):

		# continue finding grand-children until we reach an end point
		addAsBranchSegment = True
		fullSegmentFound = False
		segment = [node]

		# while there are still generations of children to traverse
		nextChild = children[x]
		while not fullSegmentFound:
			# possible end points: MERGE, BAREN, BRANCH
			# possible start points: MERGE, BRANCH. (or ORPHAN, but that would be "node" already)

			# add merge point to the queue. don't keep merge commit in the segment
			if is_merge(nextChild):
				if nextChild not in visited:
					queue.append(nextChild)

				# if there's only one item left in the branch segment and it's either
				# a merge or a branch, don't count it as a branch segment
				if len(segment) == 1 and (is_merge(segment[0]) or is_branch(segment[0])):
					addAsBranchSegment = False
				fullSegmentFound = True
					
			# add branch point to the queue.
			elif is_branch(nextChild):
				if nextChild not in visited:
					queue.append(nextChild)

				segment.append(nextChild)
				fullSegmentFound = True

			# child has no more children. we're done. add it to the queue and finish the segment
			elif is_baren(nextChild):
				visited.add(nextChild)
				segment.append(nextChild)
				fullSegmentFound = True

			# continuation point. append it to the segment, but we're not done yet
			elif is_linear(nextChild):
				segment.append(nextChild)
				visited.add(nextChild)

			# get the next child from the next generation
			if not fullSegmentFound:
				nextGeneration = dp[nextChild]
				nextChild = nextGeneration[0]


		# build up the array of all branch segments
		if addAsBranchSegment:
			branch_units.append(segment)

	# finished with all the paths stemming from this node, so it can be removed
	while stack:
		visited.add(stack.pop())

	# now that the stack's empty, grab from the queue until we reach an unvisited node
	# we may have marked some nodes from the queue as visited during our last traversal,
	# so we need to check
	foundUnvisitedNode = False
	while queue and not foundUnvisitedNode:
		nextNode = queue.popleft()

		if nextNode not in visited:
			stack.append(nextNode)
			foundUnvisitedNode = True


# go through all branch segments to diff and write those diffs to the file
COUNT = 0
for x in xrange(0,len(branch_units)):

	# quick progress update
	COUNT = COUNT + 1
	sys.stdout.write("\rDiffing " + str(COUNT) + " of " + str(len(branch_units)) + " branch segments.")
	sys.stdout.flush()

	branch_segment = branch_units[x]

	# initialization
	nextStartIndex, nextEndIndex = 0, 1
	combinedCommitLoc, combinedCommitHunk, combinedCommitFile = 0, 0, 0
	numCommits = len(branch_segment) - 1
	committers, authors = set(), set()
	commitStart, authorStart, commitEnd, authorEnd = datetime(MAXYEAR, 1, 1), datetime(MAXYEAR, 1, 1), datetime(MINYEAR, 1, 1), datetime(MINYEAR, 1, 1)


	segmentHasOrphan = (is_orphan(branch_segment[0])
	segmentOnlyHasOrphan = (segmentHasOrphan and numCommits == 1)

	# if the orphan is the only item in this list, use the showstat as the branch as unit and commit summation unit
	if segmentOnlyHasOrphan:
		o = branch_segment[1] # actual orphan, not the "NULL" that we create
		showstat = gitshell.show(o)

		authors.add(dm[o].author)
		committers.add(dm[o].committer)
		commitTime, authorTime = dm[o].commit_date, dm[o].author_date

		combinedCommitFile = len(showstat.keys())
		for f in showstat.keys():
			combinedCommitLoc += showstat[f][0] + showstat[f][1]
			combinedCommitHunk += showstat[f][2]

		if args.csv:
			w.write_commit_data("NULL", o, combinedCommitFile, combinedCommitLoc, combinedCommitHunk, commitTime, authorTime)
			w.write_branch_data("NULL", o, showstat, numCommits, len(committers), len(authors), commitTime, commitTime, authorTime, authorTime, combinedCommitLoc, combinedCommitHunk, combinedCommitFile)


	else:
		if segmentHasOrphan:
			o = branch_segment[1] # actual orphan, not the "NULL" that we create
			showstat = gitshell.show(o)
			nextStartIndex, nextEndIndex = 1, 2 # can't use a commit diff on a NULL commit

			combinedCommitFile = len(showstat.keys())
			for f in showstat.keys():
				combinedCommitLoc += showstat[f][0] + showstat[f][1]
				combinedCommitHunk += showstat[f][2]


		else:
			print "something"
		








	# to measure impact - get the branch diff, diff from start...end of the segment
	# special case: if the starting point is NULL, we created it. use git show for
	#    the following commit, and git diff for the remainder

	
	specialOrphanCase = False
	if is_orphan(branch_segment[0]):
		showstat = gitshell.show(branch_segment[0])
		specialOrphanCase = True

	else:
		start = branch_segment[0]
		end = branch_segment[len(branch_segment) - 1]
		branchdiffstat = gitshell.diff(args.repository, start, end)

	# to measure effort - get a combination of commit diffs throughout the branch segment
	# keep a total of commit metadata as we go along
	while (nextEndIndex < len(branch_segment)):
		nextStart = branch_segment[nextStartIndex]
		nextEnd = branch_segment[nextEndIndex]

		# perform commit diffs and write them out to a csv file
		commitdiffstat = gitshell.diff(args.repository, nextStart, nextEnd)

		# add up total locs, hunks, and files within that commit's diff
		commitLoc, commitHunk, commitFile = 0, 0, len(commitdiffstat.keys())
		combinedCommitFile += commitFile

		for f in commitdiffstat.keys():
			commitLoc += int(commitdiffstat[f][0]) + int(commitdiffstat[f][1])
			commitHunk += int(commitdiffstat[f][2])

		combinedCommitLoc += commitLoc
		combinedCommitHunk += commitHunk

		committers.add(dm[nextEnd].committer)
		authors.add(dm[nextEnd].author)
		cTime = dm[nextEnd].commit_date
		aTime = dm[nextEnd].author_date

		if cTime <= commitStart:
			commitStart = cTime
		if cTime >= commitEnd:
			commitEnd = cTime

		if aTime <= authorStart:
			authorStart = aTime
		if aTime >= authorEnd:
			authorEnd = aTime

		if args.csv:
			w.write_commit_data(nextStart, nextEnd, commitFile, commitLoc, commitHunk, dm[nextEnd])

		nextStartIndex = nextStartIndex + 1
		nextEndIndex = nextEndIndex + 1

	# write out branch diff stats and combined commit stats to a csv file
	if args.csv:
		w.write_branch_data(start, end, branchdiffstat, numCommits, len(committers), len(authors), commitStart, commitEnd, authorStart, authorEnd, combinedCommitLoc, combinedCommitHunk, combinedCommitFile)



# PRINT OUT HOW MANY OCTOPI THERE ARE
# PRINT OUT LOC ADD/REMOVED SEPARATELY




#
## re-traverse squished graph to write to file
#visited, queue = set(), ["NULL"]
#while queue:
#	node = queue.pop(0)
#	if node not in visited:
#		visited.add(node)
#
#		# for all children of this commit
#		for child in dp[node]:
#
#			# draw edge in graph from parent (node) to child
#			weight = 1
#			if child in cache:
#				weight = cache[child]._weight
#
#				# print diff for linear paths
#				parent = node
#				if parent == "NULL":
#					parent = cache[child]._nparent
#
#				# get the diff for the entire branch
#				branchdiffstat = gitshell.diff(args.repository, parent, child)
#
#				# get the diffs for each individual commit, starting
#				# from the parent to this child
#				lastChild = child
#				nextParent = dc[lastChild][0]
#				finishedLinearPath = False
#
#				combinedCommitLoc = 0
#				combinedCommitHunk = 0
#				combinedCommitFile = set()
#
#				while not finishedLinearPath:
#					if (nextParent == "NULL"):
#						finishedLinearPath = True
#					else:
#						commitdiffstat = gitshell.diff(args.repository, nextParent, lastChild)
#
#						# add up total locs and hunks for each file within that commit's diff
#						commitLocs = 0
#						commitHunks = 0
#						for key in commitdiffstat.keys():
#							commitLocs = commitLocs + int(commitdiffstat[key][0]) + int(commitdiffstat[key][1])
#							commitHunks = commitHunks + int(commitdiffstat[key][2])
#							combinedCommitFile.add(key)
#
#						if args.csv:
#							w.write_commit_data(nextParent, lastChild, len(commitdiffstat.keys()), commitLocs, commitHunks, dm[lastChild])
#
#						# add upt total locs and hunks to all other commits in that branch
#						combinedCommitLoc = combinedCommitLoc + commitLocs
#						combinedCommitHunk = combinedCommitHunk + commitHunks
#
#					if nextParent == parent:
#						finishedLinearPath = True
#					elif not finishedLinearPath:
#						lastChild = nextParent
#						nextParent = dc[lastChild][0]
#
#				if args.csv:
#					w.write_branch_data(node, child, branchdiffstat, cache[child], combinedCommitLoc, combinedCommitHunk, combinedCommitFile)
#
#			if args.graph:
#				gwrite(graph, child, node, weight)
#
#			# visit
#			queue.append(child)

if args.graph:
	end_graph(graph)

if args.csv:
	w.close()

if args.svg:
	dotter.draw_graph(args.output, args.svg)
