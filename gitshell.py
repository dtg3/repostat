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
	fileDiffStats = defaultdict(list)  # {"filename" : loc-add, loc-del, hunks}

	# todo: fix for init commit
	if parentSHA == "NULL":
		return fileDiffStats

	output = subprocess.check_output(['git', '--git-dir', repoPath + '/.git', 'diff', parentSHA, commitSHA,'--numstat', '--unified=0', '--find-renames']).splitlines()
	processStat = True  # whether numstat output needs processed
	totalHunks = 0      # number of hunks modified
	currentFile = ""    # file of current diff

	for line in output:

		# parse output from --numstat
		if processStat:
			if not line == "":
				stat = line.split('\t')
				fileDiffStats[stat[2]].append(stat[0]) # lines added
				fileDiffStats[stat[2]].append(stat[1]) # lines removed

			else:
				processStat = False

		# parse output from unified diff to calculate hunks
		else:
			if line.startswith("diff"):

				# store hunks from previous file diff
				if not totalHunks == 0:
					fileDiffStats[currentFile].append(str(totalHunks))
					totalHunks = 0

				# get filename of current file being diffed
				currentFile = line.split(" ")[2][2:]

			if line.startswith("@@"):
				totalHunks += 1


	# store hunks from last file diff
	fileDiffStats[currentFile].append(str(totalHunks))

	return fileDiffStats
