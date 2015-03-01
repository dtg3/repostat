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


# going bottom (first commit ever) up (most recent)
def is_branch(sha):
	return len(dp[sha]) > 1 # parent has more than one child

def is_merge(sha):
	return len(dc[sha]) > 1 # child has more than one parent

def is_orphan(sha):
	return len(dp[sha]) < 1 # has no parents

def is_init(sha):
	return sha == "NULL"

def is_linear(sha):
	return not is_init(sha) and not is_orphan(sha) and not is_merge(sha) and not is_branch(sha)

def is_force_write(sha):
	return commits[sha]._write

def force_write(sha):
	commits[sha]._write = True


# data used for tracking commits
class Data(object):
	def __init__(self):
		self._write = False
		self._weight = 0


# edges used for squashing linear branches
class Edge(object):
	_parent = ""
	_weight = 0

	def __init__(self, child, weight):
		self._parent = child
		self._weight = weight
	def fdel(self):
		del self._parent
		del self._weight


# main
parser = argparse.ArgumentParser()
parser.add_argument('repository')
args = parser.parse_args()


# first traversal for mapping parent/child relationship to build up a tree
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
dp = defaultdict(list) # dictionary where keys are parent commits
dc = defaultdict(list) # dictionary where keys are child commits
commits = {}

commits["NULL"] = Data()
for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	commits[child] = Data()
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

# re-traverse for writing to the file, starting with the first commit
visited, queue = set(), ["NULL"]
while queue:
	node = queue.pop(0)
	if node not in visited:
		visited.add(node)

		if is_branch(node) or is_merge(node) or is_init(node) or is_orphan(node):

			if is_branch(node):
				print node + " is branch!"
			elif is_merge(node):
				print node + " is merge!"
			elif is_init(node):
				print node + " is init!"
			elif is_orphan(node):
				print node + " is orphan!"
			force_write(node)
		
		if is_branch(node) or is_linear(node):
			parent = dc[node][0]
			print node + " is linear!"
			print "parent: " + parent
			print "child: " + node
			if parent in cache:
				temp = cache[parent]
				del cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1)
			else:
				cache[node] = Edge(node, 1)
			print "squishing " + node + " to " + cache[node]._parent + " with weight " + str(cache[node]._weight)

			if is_branch(node):
				gwrite(graph, node, cache[node]._parent, cache[node]._weight)
				del cache[node]

		for n in dp[node]:
			queue.append(n)

for c in commits:
	if commits[c]._write:
		for child in dp[c]:
			gwrite(graph, child, c, 1)
	elif c in cache:
		#print "squishing " + cache[c]._parent + " to " + c + " with weight " + str(cache[c]._weight)
		gwrite(graph, c, cache[c]._parent, cache[c]._weight)

graph.write('}\n')
graph.close()

#output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
#for line in output:
#	SHAS = line.strip("\"").split(' ')
#
#	child = SHAS[0]
#	parents = SHAS[1:]
#
#	# TODO: missing something here, or writing something the wrong way.
#	# the graph is all goofy, and nodes point to nodes they shouldn't.
#	# investigate.
#
#	is_branch = False
#	for p in parents:
#		if len(dp[p]) > 1:
#			is_branch = True
#
#	is_init = False
#	for p in parents:
#		if not p:
#			is_init = True
#
#	is_linear = False
#	if len(parents) == 1 and len(dp[parents[0]]) == 1:
#		is_linear = True
#
#	# merge
#	if len(parents) >= 2:
#		for p in parents:
#			gwrite(graph, child, p, 1)
#			if p in cache:
#				gwrite(graph, cache[p]._parent, cache[p]._weight)
#				del cache[p]
#
#	# branch
#	elif is_branch:
#		for p in parents:
#			gwrite(graph, child, p, 1)
#			if p in cache:
#				gwrite(graph, cache[p]._parent, cache[p]._weight)
#				del cache[p]
#
#	# init
#	elif is_init:
#		for p in parents:
#			gwrite(graph, child, p, 1)
#			if p in cache:
#				gwrite(graph, cache[p]._parent, cache[p]._weight)
#				del cache[p]
#
#	# linear
#	elif is_linear:
#		p = parents[0]
#		if child in cache:
#			cache[p] = Edge(cache[child]._parent, cache[child]._weight + 1)
#			del cache[child]
#		else:
#			cache[p] = Edge(child, 1)
#
#	# wtf
#	else:
#		print "ABORT! AHH! JUMP SHIP!"
#

# write anything left remaining in the cache
#for key in cache:
#	gwrite(graph, key, cache[key]._parent, cache[key]._weight)
#
#graph.write('}\n')
#graph.close()


