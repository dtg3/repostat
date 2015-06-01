from metadata import Metadata
import subprocess
from collections import defaultdict
import re
import utils as utils

def build_commit_dicts(repoPath):

	# create the null commit for the lattice
	empty_tree = subprocess.check_output(['git', '--git-dir', repoPath, 'hash-object', '-t', 'tree', '/dev/null']).splitlines()
	NULL = empty_tree[0]   # magic number 4b825dc642cb6eb9a060e54bf8d69288fbee4904

	dp = defaultdict(list) # dictionary where keys are parent commits
	dc = defaultdict(list) # dictionary where keys are child commits
	dmetadata = dict()     # dictionary where keys are commmits and values is metadata on it
	
	output = subprocess.check_output(['git', '--git-dir', repoPath, 'log', '--branches', '--date=iso', '--pretty=format:"%cN<delim>%aN<delim>%cd<delim>%ad<delim>%H<delim>%P<delim>%s<delim>%b<delim>"'])
	data = output.split('<delim>')

	# iterate through each delimited field - every 8 field marks the next commit metadata
	index = 0
	while ((index + 7) < len(data)):
		# grab metadata from the first 8 delimited results
		committer    = data[index].strip().strip('\"').strip().strip('\"') # STRIP IT ALL!!!!!!! (but really, without all strips a leading quote is left)
		author       = data[index + 1].strip().strip('\"')
		commit_date  = utils.normalize_datetime(data[index + 2])
		author_date  = utils.normalize_datetime(data[index + 3])
		child        = data[index + 4]
		parents      = data[index + 5].split()
		subject      = data[index + 6].strip().strip('\"')
		body         = data[index + 7].strip().strip('\"')
		dmetadata[child] = Metadata(committer, author, commit_date, author_date, subject, body)

		# build child/parent dictionaries
		for p in parents:
			if p:
				dp[p].append(child)
				dc[child].append(p)

		if len(parents) == 0:
			dp[NULL].append(child)
			dc[child].append(NULL)

		index += 8

	return NULL, dp, dc, dmetadata


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
				elif "\"b/" in line:
					currentFile = line.strip('"')[line.index("\"b/") + 3:]
				elif "b/" in line:
					currentFile = line.strip('"')[line.index("b/") + 2:]

			# update that file's number of hunks modified as they're encountered
			if line.startswith("@@"):
				fileDiffStats[currentFile][2] = str( int(fileDiffStats[currentFile][2]) + 1 )

	return fileDiffStats
