import subprocess

# writing to graph is a tad iffy
class Dotter(object):
	graph = None
	dotFile = ""

	def __init__(self, outputFile):
		self.svgFile = outputFile + ".svg"
		self.dotFile = outputFile + ".dot"
		self.graph = open(self.dotFile, "wb")
		self.graph.write('graph TD {\n')
		
	def end(self):
		self.graph.write('};')
		self.graph.close()
		self.draw()

	# draw svg based on dot file. must be called after end()
	def draw(self):
		dot = subprocess.Popen(["dot", "-v", "-Tsvg", self.dotFile, "-o", self.svgFile], 
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			line = dot.stdout.readline()
			if not line:
				break
			print line

	# write to dot file
	def gwrite(self, child, parent, weight):
		if not parent:
			self.graph.write('\t\"NULL\" --> \"' + child + '\";\n')
		elif weight == 1:
			self.graph.write('\t\"' + parent + '\" --> \"' + child + '\";\n')
		elif weight > 1:
			self.graph.write('\t\"' + parent + '\" --> ' + '|' + str(weight) + '| \"' + child + '\";\n')

