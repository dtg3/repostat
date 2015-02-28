#!/usr/bin/python

#run me from the git repo root
import subprocess
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('repository')
args = parser.parse_args()


# first traversal for mapping parent/child relationship to build up a tree
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
d = defaultdict(list)

for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	for p in parents:
		if p:
			d[p].append(child)


graph = open("graph.dot", "wb")
graph.write('digraph G {\n')
graph.write('\trankdir="BT"\n')

# re-traverse for writing to the file
output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	for parent in parents:
		if parent:
			graph.write('\t"' + child + '" -> "' + parent + '";\n')


graph.write('}\n')
graph.close()

