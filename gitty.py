#!/usr/bin/python

#run me from the git repo root
import subprocess
import argparse
from collections import defaultdict

# write to dot graph
def gwrite(graph, child, parent, weight):
	if not parent:
		graph.write('\t"NULL" -> "' + child + '";\n')
	elif weight == 1:
		graph.write('\t"' + parent + '" -> "' + child + '";\n')
	elif weight > 1:
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
	return not is_init(sha) and not is_merge(sha) and not is_branch(sha)

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
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%h %p"']).splitlines()
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
	print "CHECKING " + node
	if node not in visited:
		visited.add(node)

		if is_branch(node) or is_merge(node) or is_init(node) or is_orphan(node):

			if is_branch(node):
				print node + " is branch!"
			elif is_merge(node):
				print node + " is merge!"
				for parent in dc[node]:
					if parent in cache:
						print "parent is linear!"
						gwrite(graph, parent, cache[parent]._parent, cache[parent]._weight)
						del cache[parent]
					gwrite(graph, node, parent, 1)
			elif is_init(node):
				print node + " is init!"
			elif is_orphan(node):
				print node + " is orphan!"
			force_write(node)

		
		if not is_init(node):
			parent = dc[node][0]
			if parent in cache:
				temp = cache[parent]
				del cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1)
			else:
				cache[node] = Edge(node, 0)
			print "squishing " + node + " to " + cache[node]._parent + " with weight " + str(cache[node]._weight)

			print node + " is linear! parent is: " + cache[node]._parent

			if is_branch(node):
				gwrite(graph, node, cache[node]._parent, cache[node]._weight)
				del cache[node]

		# then visit the children of this commit
		for n in dp[node]:
			queue.append(n)
		print "queue is now at: " + str(queue)

	else:
		print node + " has been checked already"

for c in commits:
	if commits[c]._write:
		for child in dp[c]:
			gwrite(graph, child, c, 1)
	elif c in cache:
		#print "squishing " + cache[c]._parent + " to " + c + " with weight " + str(cache[c]._weight)
		gwrite(graph, c, cache[c]._parent, cache[c]._weight)

graph.write('}\n')
graph.close()

