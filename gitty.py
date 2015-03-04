#!/usr/bin/python

#run me from the git repo root
import argparse
import gitshell

def init_graph(outputFile):
	graph = open(outputFile, "wb")
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
	return not is_init(sha) and not is_merge(sha) and not is_branch(sha)

# pre-condition: sha is linear
def is_first_linear(sha):
	return not is_linear(dc[sha][0]) # if parent isn't linear

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


# edges used for squishing linear branches
class Edge(object):
	_parent = ""
	_weight = 1

	def __init__(self, p, weight):
		self._parent = p
		self._weight = weight
	def fdel(self):
		del self._parent
		del self._weight


# main
parser = argparse.ArgumentParser()
parser.add_argument('repository')
parser.add_argument('-o','--output', type=str, default="graph.dot")
args = parser.parse_args()


# first traversal for mapping parent/child relationship to build up a tree
dp, dc = gitshell.buildCommitDicts(args.repository)

cache = dict() # cache of unwritted linear squashes (farthest parent -> original child, weight)
graph = init_graph(args.output) # dot graph

# re-traverse for marking what to write to the file, starting with the first commit using BFS
visited, queue = set(), ["NULL"]
while queue:
	node = queue.pop(0)
	if node not in visited:
		visited.add(node)

		debug_what_am_i(node)

		if is_linear(node):
			parent = dc[node][0]
			if is_first_linear(node):
				# create edge from parent ending at current node, weight = 1
				# remove old edge, put new edge ending at this commit (no op)
				cache[node] = Edge(parent, 1)

			else:
				# extend parent's squished parent to end at current node, weight + 1
				temp = cache[parent]
				cache[node] = Edge(temp._parent, temp._weight + 1)
				del cache[parent]

				# remove old edge, put new edge ending at this commit
				dp[temp._parent].remove(parent)
				dp[temp._parent].append(node)

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
			gwrite(graph, child, node, weight)

			# visit
			queue.append(child)

end_graph(graph)

