#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell
import dotter
from edge import Edge
from writer import Writer

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

def is_bare(sha):
	return len(dp[sha]) < 1 # has no parents

def is_orphan(sha):
	# todo: we /assume/ it's the first commit, but really it's just a commit
	# with no parents. there can be multiple commits like this in a repo. need
	# a better method of detection
	return sha == "NULL"    # first commit

def is_linear(sha):
	return not is_orphan(sha) and not is_merge(sha) and not is_branch(sha)

# pre-condition: sha is linear
def is_first_linear(sha):
	return not is_linear(dc[sha][0]) # if parent isn't linear

def debug_what_am_i(sha):
	if is_branch(sha):
		print sha + " is branch!"
	if is_merge(sha):
		print sha + " is merge!"
	if is_orphan(sha):
		print sha + " is init!"
	if is_bare(sha):
		print sha + " is orphan!"
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

# first traversal for mapping parent/child relationship to build up a tree
dp, dc, cache, dm = gitshell.build_commit_dicts(args.repository)

if args.graph:
	graph = init_graph(args.graph) # dot graph

if args.csv:
	w = Writer(args.csv)
	w.write_headers()

# re-traverse for marking what to write to the file, starting with the first commit using BFS
visited, queue = set(), ["NULL"]
while queue:
	node = queue.pop(0)
	if node not in visited:
		visited.add(node)

		#debug_what_am_i(node)

		if is_linear(node):
			parent = dc[node][0]
			if is_first_linear(node):
				# create edge from parent ending at current node, weight = 1
				# remove old edge, put new edge ending at this commit (no op)
				cache[node] = Edge(parent, 1, '')

				# store metadata
				cache[node].committers.add(dm[node].committer)
				cache[node].authors.add(dm[node].author)
				#cache[node].files.add(dm[node].files)
				#locByBranch = 0
				#locByCommitSum = 0
				#hunkByBranch = 0
				#hunkByCommitSum = 0
				cache[node].commitStartTime = dm[node].commit_date
				cache[node].commitEndTime = dm[node].commit_date
				cache[node].authorStartTime = dm[node].author_date
				cache[node].authorEndTime = dm[node].author_date

			else:
				# extend parent's squished parent to end at current node, weight + 1
				temp = cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1, temp._nparent)
				cache[node].committers.add(dm[node].committer)
				cache[node].authors.add(dm[node].author)
				cache[node].commitEndTime = dm[node].commit_date
				cache[node].authorEndTime = dm[node].author_date
				del cache[parent]

				# remove old edge, put new edge ending at this commit
				dp[temp._parent].remove(parent)
				dp[temp._parent].append(node)

			if is_orphan(parent):
				cache[node]._nparent = node

		# then visit the children of this commit
		for n in dp[node]:
			queue.append(n)

# re-traverse squished graph to write to file
visited, queue = set(), ["NULL"]
while queue:
	node = queue.pop(0)
	if node not in visited:
		visited.add(node)

		# for all children of this commit
		for child in dp[node]:

			# draw edge in graph from parent (node) to child
			weight = 1
			if child in cache:
				weight = cache[child]._weight

				# print diff for linear paths
				parent = node
				if parent == "NULL":
					parent = cache[child]._nparent

				diffstat = gitshell.diff(args.repository, parent, child)

				# TODO: turn diffstat into a part of cache here

				if args.csv:
					w.write_data(node, child, diffstat, cache[child])
					#write_csv(diffstat, bu_csv)
					#write_csv(diffstat, bc_csv)
					#write_csv(diffstat, cu_csv)

			if args.graph:
				gwrite(graph, child, node, weight)

			# visit
			queue.append(child)

if args.graph:
	end_graph(graph)

if args.csv:
	w.close()

if args.svg:
	dotter.draw_graph(args.output, args.svg)
