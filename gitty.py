#!/usr/bin/python

#run me from the git repo root
import subprocess
import argparse
from collections import defaultdict

# write to dot graph
def gwrite(graph, child, parent, weight):
	if not parent:
		graph.write('\t"NULL" -> "' + child + '";\n')
	elif weight <= 1:
		graph.write('\t"' + parent + '" -> "' + child + '";\n')
	else:
		graph.write('\t"' + parent + '" -> "' + child + '" [label="' + str(weight) + '"];\n')

# edges used for squashing linear branches
class Edge(object):
	_child = ""
	_weight = 0

	def __init__(self, child, weight):
		self._child = child
		self._weight = weight
	def fget(self):
		return self._child, self._weight
	def fset(self, parent, weight):
		self._child = child
		self._weight = weight
	def fdel(self):
		del self._child
		del self._weight


# main
parser = argparse.ArgumentParser()
parser.add_argument('repository')
args = parser.parse_args()


# first traversal for mapping parent/child relationship to build up a tree
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
dp = defaultdict(list) # dictionary where keys are parent commits
dc = defaultdict(list) # dictionary where keys are child commits

for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	for p in parents:
		if p:
			dp[p].append(child)
			dc[child].append(p)
		else:
			dp["NULL"].append(child)
			dc[child].append("NULL")

# cache of unwritted linear squashes (farthest parent -> original child, weight)
cache = dict()

graph = open("graph.dot", "wb")
graph.write('digraph G {\n')
graph.write('\trankdir="BT"\n')

# re-traverse for writing to the file
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	# TODO: missing something here, or writing something the wrong way.
	# the graph is all goofy, and nodes point to nodes they shouldn't.
	# investigate.

	is_branch = False
	for p in parents:
		if len(dp[p]) > 1:
			is_branch = True

	is_init = False
	for p in parents:
		if not p:
			is_init = True

	is_linear = False
	if len(parents) == 1 and len(dp[parents[0]]) == 1:
		is_linear = True

	# merge
	if len(parents) >= 2:
		for p in parents:
			gwrite(graph, child, p, 1)
			if p in cache:
				gwrite(graph, cache[p]._child, cache[p]._weight)
				del cache[p]

	# branch
	elif is_branch:
		for p in parents:
			gwrite(graph, child, p, 1)
			if p in cache:
				gwrite(graph, cache[p]._child, cache[p]._weight)
				del cache[p]

	# init
	elif is_init:
		for p in parents:
			gwrite(graph, child, p, 1)
			if p in cache:
				gwrite(graph, cache[p]._child, cache[p]._weight)
				del cache[p]

	# linear
	elif is_linear:
		p = parents[0]
		if child in cache:
			cache[p] = Edge(cache[child]._child, cache[child]._weight + 1)
			del cache[child]
		else:
			cache[p] = Edge(child, 1)

	# wtf
	else:
		print "ABORT! AHH! JUMP SHIP!"


# write anything left remaining in the cache
for key in cache:
	gwrite(graph, key, cache[key]._child, cache[key]._weight)

graph.write('}\n')
graph.close()


