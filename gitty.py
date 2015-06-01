#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell
import dotter
import sys
from jsoner import Jsoner
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
	return sha == NULL      # first commit

def is_linear(sha):
	return len(dp[sha]) == 1 and len(dc[sha]) == 1 # has one parent and one child

def is_octopus(sha):
	return len(dp[sha]) > 2 # has more than two parents, octopus merge required

def apply_gitshell(commitdiffstat):
	nextParent = commitdiffstat[1]
	lastChild = commitdiffstat[2]

	commitdiffstatp = gitshell.diff(args.repository, nextParent, lastChild)
	commitdiffstat[0] = commitdiffstatp

	return commitdiffstat

def debug_what_am_i(sha):
	if is_branch(sha):
		print sha + " is branch"
	if is_merge(sha):
		print sha + " is merge"
	if is_orphan(sha):
		print sha + " is orphan"
	if is_baren(sha):
		print sha + " is bare"
	if is_linear(sha):
		print sha + " is linear"

# main
parser = argparse.ArgumentParser()
parser.add_argument('repository')
parser.add_argument('-s','--svg', type=str)
parser.add_argument('-g','--graph', type=str)
parser.add_argument('-c','--csv', type=str)
parser.add_argument('-j','--json', type=str)

args = parser.parse_args()

# first traversal for mapping parent/child relationship to build up a tree
NULL, dp, dc, dm = gitshell.build_commit_dicts(args.repository)

# find all octopi
octopi = 0
for sha in dp:
	if is_octopus(sha):
		octopi += 1

if args.graph:
	graph = init_graph(args.graph) # dot graph

if args.csv:
	w = Writer(args.csv)
	w.write_headers()
	w.write_repo_stats("octopi", octopi)

if args.json:
	j = Jsoner(args.json)

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
pool = Pool(processes=8)
for x in xrange(0,len(branch_units)):

	# quick progress update
	COUNT = COUNT + 1
	sys.stdout.write("\rDiffing " + str(COUNT) + " of " + str(len(branch_units)) + " branch segments.")
	sys.stdout.flush()

	branch_segment = branch_units[x]

	# initialization
	nextStartIndex, nextEndIndex = 0, 1
	combinedCommitLocA, combinedCommitLocR, combinedCommitHunk, combinedCommitFile = 0, 0, 0, set()
	numCommits = len(branch_segment) - 1
	committers, authors = set(), set()
	commitStart, authorStart, commitEnd, authorEnd = datetime(MAXYEAR, 1, 1), datetime(MAXYEAR, 1, 1), datetime(MINYEAR, 1, 1), datetime(MINYEAR, 1, 1)

	# to measure impact - get the branch diff, diff from start...end of the segment
	start = branch_segment[0]
	end = branch_segment[numCommits]

	if args.graph:
		gwrite(graph, start, end, numCommits)

	branchdiffstat = gitshell.diff(args.repository, start, end)

	# to measure effort - get a combination of commit diffs throughout the branch segment
	# keep a total of commit metadata as we go along
	commitdiffstats = []
	while (nextEndIndex < len(branch_segment)):
		nextStart = branch_segment[nextStartIndex]
		nextEnd = branch_segment[nextEndIndex]

		commitdiffstats.append([0, nextStart, nextEnd])

		nextStartIndex = nextStartIndex + 1
		nextEndIndex = nextEndIndex + 1

	# perform commit diffs and write them out to a csv file
	commitdiffstats = pool.map(apply_gitshell, (commitdiffstats))

	if args.json:
		j.addSegment()

	for cdata in commitdiffstats:
		commitdiffstat = cdata[0]
		nextStart = cdata[1]
		nextEnd = cdata[2]

		# add up total locs, hunks, and files within that commit's diff
		commitLocA, commitLocR, commitHunk, commitFile = 0, 0, 0, len(commitdiffstat.keys())
		for f in commitdiffstat.keys():
			commitLocA += int(commitdiffstat[f][0])
			commitLocR += int(commitdiffstat[f][1])
			commitHunk += int(commitdiffstat[f][2])
			combinedCommitFile.add(f)

		combinedCommitLocA += commitLocA
		combinedCommitLocR += commitLocR
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
			w.write_commit_data(nextStart, nextEnd, commitFile, commitLocA, commitLocR, commitHunk, cTime, aTime)

		if args.json:
			json_cstats = j.formDiffStats(commitLocA, commitLocR, commitHunk, commitdiffstat.keys())
			json_commit = j.formCommitStats(dc[nextEnd], dp[nextEnd], dm[nextEnd].committer, dm[nextEnd].author, cTime, aTime, dm[nextEnd].msg, dm[nextEnd].body, "origin todo", json_cstats)
			j.addCommitToLastSegment(nextEnd, json_commit)

	# write out branch segment and commits info to json object
	if args.json:
		json_bstats = j.formDiffStats(combinedCommitLocA, combinedCommitLocR, combinedCommitHunk, combinedCommitFile)
		j.addEuclideanToLastSegment(json_bstats)

	# write out branch diff stats and combined commit stats to a csv file
	if args.csv:
		w.write_branch_data(start, end, branchdiffstat, numCommits, len(committers), len(authors), commitStart, commitEnd, authorStart, authorEnd, combinedCommitLocA, combinedCommitLocR, combinedCommitHunk, len(combinedCommitFile))

if args.graph:
	end_graph(graph)

if args.csv:
	w.close()

if args.svg:
	dotter.draw_graph(args.output, args.svg)

if args.json:
	j.finish()

