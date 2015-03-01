#!/usr/bin/python

#run me from the git repo root
import subprocess
import argparse
from collections import defaultdict

def init_graph():
	graph = open("graph.dot", "wb")
	graph.write('digraph G {\n')
	graph.write('\trankdir="BT"\n')
	return graph

def end_graph(graph):
	graph.write('}\n')
	graph.close()

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
	return sha == "NULL"    # first commit

def is_linear(sha):
	# todo: this may be wrong
	return not is_init(sha) and not is_merge(sha) and not is_branch(sha)

def is_force_write(sha):
	return commits[sha]._write

def force_write(sha):
	commits[sha]._write = True

def is_any_parent_force_write(sha):
	for p in dc[sha]:
		if commits[sha]._write:
			return True
	return False

def is_squishable(sha):
	# todo: implement
	return False


def debug_what_am_i(sha):
	if is_branch(sha):
		print sha + " is branch!"
	if is_merge(sha):
		print sha + " is merge!"
	if is_init(sha):
		print sha + " is init!"
	if is_orphan(sha):
		print sha + " is orphan!"
	if is_linear(sha):
		print sha + " is linear!"

# data used for tracking commits
class Data(object):
	def __init__(self):
		self._write = False


# edges used for squashing linear branches
class Edge(object):
	_parent = ""
	_weight = 0

	def __init__(self, p, weight):
		self._parent = p
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
commits = {}           # dictionary of all commits, whether they should be written

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

cache = dict() # cache of unwritted linear squashes (farthest parent -> original child, weight)
graph = init_graph() # dot graph

# re-traverse for writing to the file, starting with the first commit using BFS
visited, queue = set(), ["NULL"]
while queue:
	node = queue.pop(0)
	if node not in visited:
		visited.add(node)

		debug_what_am_i(node)

		# todo: squish
		force_write(node)

		#if is_branch(node) or is_merge(node) or is_init(node) or is_orphan(node):
		#	force_write(node)

		if is_squishable(node):
			parent = dc[node][0]
			if parent in cache:
				temp = cache[parent]
				del cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1)
			else:
				cache[node] = Edge(node, 0)
			print "squishing " + node + " to " + cache[node]._parent + " with weight " + str(cache[node]._weight)


		# then visit the children of this commit
		for n in dp[node]:
			queue.append(n)

# write out only those commits that we marked should be written
for c in commits:
	if commits[c]._write:
		for child in dp[c]:
			gwrite(graph, child, c, 1)
	elif c in cache:
		gwrite(graph, c, cache[c]._parent, cache[c]._weight)

end_graph(graph)

