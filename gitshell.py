import subprocess
from collections import defaultdict

def buildCommitDicts(repoPath):
	output = subprocess.check_output(['git', '--git-dir', repoPath + '/.git', 'log', '--branches', '--pretty=format:"%h %p"']).splitlines()
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

	return dp, dc

def diff(repoPath, parentSHA, commitSHA):
	output = subprocess.check_output(['git', '--git-dir', repoPath + '/.git', 'diff', parentSHA, commitSHA,'--numstat', '--unified=0', '--find-renames']).splitlines()
	processStat = True
	totalHunks = 0

	fileDiffStats = defaultdict(list)

	currentFile = ""
	for line in output:
		if processStat:
			if not line == "":
				stat = line.split('\t')

				#Store filename
				fileDiffStats[stat[2]].append(stat[0]) #Store Adds
				fileDiffStats[stat[2]].append(stat[1]) #Store Removes
			else:
				processStat = False
		else:
			if line.startswith("diff"):
				if not totalHunks == 0:
					fileDiffStats[currentFile].append(str(totalHunks)) #Store Hunks
					totalHunks = 0
				currentFile = line.split(" ")[2][2:]
			if line.startswith("@@"):
				totalHunks += 1
	fileDiffStats[currentFile].append(str(totalHunks)) #Need to store final hunk total

	for key in fileDiffStats.keys():
		print key
		for item in fileDiffStats[key]:
			print item
