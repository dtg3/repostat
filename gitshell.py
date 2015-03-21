from metadata import Metadata
import subprocess
from collections import defaultdict
import re


def build_commit_dicts(repoPath):
	output = subprocess.check_output(['git', '--git-dir', repoPath, 'log', '--branches', '--date=iso', '--pretty=format:"%cN<delim>%aN<delim>%cd<delim>%ad<delim>%H<delim>%P"']).splitlines()
	dp = defaultdict(list) # dictionary where keys are parent commits
	dc = defaultdict(list) # dictionary where keys are child commits
	cache = dict()         # cache of unwritted linear squashes (farthest parent -> original child, weight)
	dmetadata = dict()     # dictionary where keys are commmits and values is metadata on it

	for line in output:
		results = line.strip("\"").split('<delim>')
		
		committer    = results[0]
		author       = results[1]
		commit_date  = results[2]
		author_date  = results[3]
		child        = results[4]
		parents      = results[5].split()

		commitMetadata = Metadata(committer, author, commit_date, author_date)
		dmetadata[child] = commitMetadata

		for p in parents:
			if p:
				dp[p].append(child)
				dc[child].append(p)

		if len(parents) == 0:
			dp["NULL"].append(child)
			dc[child].append("NULL")

	return dp, dc, cache, dmetadata


# pre-compiled regexes used in diff()
r1 = re.compile(r"([^\{]*)\{?([^\s]*)[\s=>]*([^\}]*)\}?(.*)?") # find "[name/]?[{old => new}]?[/name]?"
r2 = re.compile('//')                                          # fix up extra '//'s from previous re
r3 = re.compile(r"[^\s]*\s=>\s(.*)")                           # find "old => new"

def diff(repoPath, parentSHA, commitSHA):
	fileDiffStats = defaultdict(list)  # {"filename" : loc-add, loc-del, hunks}

	output = subprocess.check_output(['git', '--git-dir', repoPath, 'diff', parentSHA, commitSHA,'--numstat', '--unified=0', '--find-renames']).splitlines()
	processStat = True  # whether numstat output needs processed
	totalHunks = 0      # number of hunks modified
	currentFile = ""    # file of current diff

	for line in output:

		# parse output from --numstat
		if processStat:
			if not line == "":
				stat = line.split('\t')
				fileName = stat[2].strip('"')

				### enter slow-mo.
				# these regexes are the slowest thing in here so far. it would be ideal
				# if we could narrow them down into just ONE regex, or even better, to tell
				# diff that we only want the new name of the file - not both old and new.
				#
				# the following takes the file name as provided by --numstat (which, if the
				# file was renamed/moved, will give you both the old name and the new name)
				# and makes sure that we only store the new name of the file, as that is what
				# we use when counting up all the hunks.

				fileName = r1.sub("\g<1>\g<3>\g<4>", fileName)
				fileName = r2.sub('/', fileName) # idk regex D:

				# file was renamed completely, such that there were no "{" or "}"
				if "=>" in fileName:
					fileName = r3.sub("\g<1>", fileName)

				###

				linesAdded = "0" if "-" in stat[0] else stat[0]
				linesRemoved = "0" if "-" in stat[1] else stat[1]

				fileDiffStats[fileName].append(linesAdded)
				fileDiffStats[fileName].append(linesRemoved)
				fileDiffStats[fileName].append("0") # hunks

			else:
				processStat = False

		# parse output from unified diff to calculate hunks
		else:
			# get filename of current file being diffed
			if line.startswith("diff"):
				if " b/" in line:
					currentFile = line.strip('"')[line.index(" b/") + 3:]

			# update that file's number of hunks modified as they're encountered
			if line.startswith("@@"):
				fileDiffStats[currentFile][2] = str( int(fileDiffStats[currentFile][2]) + 1 )

	return fileDiffStats
