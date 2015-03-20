#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell
import dotter

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


def init_csv(filename):
	csv = open(filename, 'w')
	csv.write('merge-base,child,file,lines-added,line-removed,hunks\n')
	return csv

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


# edges used for squishing linear branches
class Edge(object):
	_parent = ""
	_weight = 1
	_nparent = "" # for cases when _parent is NULL

	def __init__(self, p, weight, np):
		self._parent = p
		self._weight = weight
		self._nparent = np
		
	def fdel(self):
		del self._parent
		del self._weight


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
dp, dc, cache = gitshell.build_commit_dicts(args.repository)

if args.graph:
	graph = init_graph(args.graph) # dot graph

if args.csv:
	csvfile = init_csv(args.csv)    # csv file with data on linear paths

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

			else:
				# extend parent's squished parent to end at current node, weight + 1
				temp = cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1, temp._nparent)
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

				if args.csv:
					write_csv(diffstat, csvfile)

			if args.graph:
				gwrite(graph, child, node, weight)

			# visit
			queue.append(child)

if args.graph:
	end_graph(graph)

if args.csv:
	csvfile.close()

if args.svg:
	dotter.draw_graph(args.output, args.svg)
