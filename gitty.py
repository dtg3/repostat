#run me from the git repo root

import subprocess

graph = open("graph.dot", "wb")
graph.write('digraph G {\n')
graph.write('\trankdir="BT"\n')

output = subprocess.check_output(['git', 'rev-list', '--remotes', '--pretty=format:"%h %p"']).splitlines()
for line in output:
	if not 'commit' in line.strip().strip("\""):
		SHAS = line.strip().strip("\"").split(' ')
		for sha in SHAS[1:]:
			graph.write('\t\"' + SHAS[0] + '\"->\"' + sha + '\";\n')

graph.write('}\n')
graph.close()

