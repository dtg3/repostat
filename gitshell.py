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