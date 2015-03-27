#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell
import dotter
import sys
from edge import Edge
from writer import Writer
from collections import deque
from datetime import datetime, timedelta, MINYEAR, MAXYEAR

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

#def is_linear(sha):
#	return not is_orphan(sha) and not is_merge(sha) and not is_branch(sha)

def is_linear(sha):
	return len(dp[sha]) == 1 and len(dc[sha]) == 1 # has one parent and one child

def is_end_point(sha):
	return is_baren(sha) or is_merge(sha) or is_branch(sha)

# pre-condition: sha is linear
def is_first_linear(sha):
	return not is_linear(dc[sha][0]) # or is_branch(dc[sha][0]) # if parent isn't linear

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



# progress updater
COUNT = 0

# go through all branch segments to diff and write those diffs to the file
for x in xrange(0,len(branch_units)):

	# progress updater
	sys.stdout.write( "\rDiffing " + str(COUNT) + " of " + str(len(branch_units)) )
	sys.stdout.flush()

	branch_segment = branch_units[x]

	numCommits = len(branch_segment) - 1
	combinedCommitLoc, combinedCommitHunk, combinedCommitFile = 0, 0, 0
	committers, authors = set(), set()
	commitStart, authorStart, commitEnd, authorEnd = datetime(MAXYEAR,1,1), datetime(MAXYEAR,1,1), datetime(MINYEAR,1,1), datetime(MINYEAR,1,1)






	# to measure impact - get the branch diff, diff from start...end of the segment
	# special case: if the starting point is NULL, we created it. grab the next one
	#   as the starting point.
	start = branch_segment[0]
	if is_orphan(start):
		start = branch_segment[1]
	end = branch_segment[len(branch_segment) - 1]

	branchdiffstat = gitshell.diff(args.repository, start, end)

	# to measure effort - get a combination of commit diffs throughout the branch segment
	# keep a total of commit metadata as we go along
	combinedCommitLoc = 0
	combinedCommitHunk = 0
	combinedCommitFile = 0
	committers = set()
	authors = set()
	commitStart = datetime.now()
	commitEnd = datetime.now()
	authorStart = datetime.now()
	authorEnd = datetime.now()

	nextStartIndex = 0
	nextEndIndex = 1
	while (nextEndIndex < len(branch_segment)):
		nextStart = branch_segment[nextStartIndex]
		nextEnd = branch_segment[nextEndIndex]

		commitdiffstat = gitshell.diff(args.repository, nextStart, nextEnd)
		cAuthor = dm[nextEnd].author
		cCommitter = dm[nextEnd].committer
		cCommitTime = dm[nextEnd].commit_date
		cAuthorTime = dm[nextEnd].author_date


		# perform commit diffs and write them out to a csv file
		if args.csv:


		++nextStartIndex
		++nextEndIndex

	# write out branch diff stats and combined commit stats to a csv file
	if args.csv:
		w.write_branch_data(start, end, branchdiffstat, numCommits, len(committers), len(authors), commitStart, commitEnd, authorStart, authorEnd, combinedCommitLoc, combinedCommitHunk, combinedCommitFile)

# re-traverse for marking what to write to the file, starting with the first commit using BFS
#visited, queue = set(), ["NULL"]
#while queue:
#	node = queue.pop(0)
#	if node not in visited:
#		visited.add(node)
#
#		debug_what_am_i(node)
#
#
#		if is_linear(node):
#			parent = dc[node][0]
#			if is_first_linear(node):
#				# create edge from parent ending at current node, weight = 1
#				# remove old edge, put new edge ending at this commit (no op)
#				cache[node] = Edge(parent, 1, '')
#
#				# store metadata
#				cache[node].committers.add(dm[node].committer)
#				cache[node].authors.add(dm[node].author)
#				cache[node].commitStartTime = dm[node].commit_date
#				cache[node].commitEndTime = dm[node].commit_date
#				cache[node].authorStartTime = dm[node].author_date
#				cache[node].authorEndTime = dm[node].author_date
#
#			else:
#				# extend parent's squished parent to end at current node, weight + 1
#				temp = cache[parent]
#				cache[node] = temp
#				cache[node]._weight = temp._weight + 1
				#
#				cache[node].committers.add(dm[node].committer)
#				cache[node].authors.add(dm[node].author)
#
#				# replace the author and commit start time if, in rewriting git
#				# or oddities with parallel dev, this commit has an earlier time
#				# than the parent commit
#				if dm[node].commit_date <= cache[node].commitStartTime:
#					cache[node].commitStartTime = dm[node].commit_date
#
#				if dm[node].author_date <= cache[node].authorStartTime:
#					cache[node].authorStartTime = dm[node].author_date
				#
#				# only replace the end times if this commit has a later date
#				if dm[node].commit_date >= cache[node].commitEndTime:
#					cache[node].commitEndTime = dm[node].commit_date
#
#				if dm[node].author_date >= cache[node].authorEndTime:
#					cache[node].authorEndTime = dm[node].author_date
#
#				del cache[parent]
#
#				# remove old edge, put new edge ending at this commit
#				dp[temp._parent].remove(parent)
#				dp[temp._parent].append(node)
#
#			if is_orphan(parent):
#				cache[node]._nparent = node
#
#		# then visit the children of this commit
#		for n in dp[node]:
#			queue.append(n)
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
