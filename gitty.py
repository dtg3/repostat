#run me from the git repo root

import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('repository')
args = parser.parse_args()


graph = open("graph.dot", "wb")
graph.write('digraph G {\n')
graph.write('\trankdir="BT"\n')


output = subprocess.check_output(['git', '--git-dir', args.repository + '/.git', 'log', '--branches', '--pretty=format:"%H %P"']).splitlines()
for line in output:
	SHAS = line.strip("\"").split(' ')

	child = SHAS[0]
	parents = SHAS[1:]

	for parent in parents:
		if parent:
			print child + " -> " + parent
			graph.write('\t"' + child + '" -> "' + parent + '";\n')

graph.write('}\n')
graph.close()

