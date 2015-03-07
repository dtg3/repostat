import subprocess

def draw_graph(inputFile, outputFile):

	dot = subprocess.Popen(["dot", "-v", "-Tsvg", inputFile, "-o", outputFile + ".svg"], 
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	while True:
		line = dot.stdout.readline()
		if not line:
			break
		print line