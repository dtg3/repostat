
import csv
import argparse
from operator import itemgetter
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument('branchcsv')
parser.add_argument('commitcsv')
args = parser.parse_args()

with open(args.branchcsv, 'rb') as fbranch:
    breader = csv.reader(fbranch)
    branches = list(breader)
    branches.pop(0) # get rid of header

with open(args.commitcsv, 'rb') as fcommits:
    creader = csv.reader(fcommits)
    commits = list(creader)
    commits.pop(0) # get rid of header


# index into branch csv file
BRANCH_ID = 0
COMMIT_START = 16
COMMIT_END = 17
COMMIT_WINDOW = 18
AUTHOR_START = 19
AUTHOR_END = 20
AUTHOR_WINDOW = 21

# index into commit csv file
COMMIT_TIME = 4
AUTHOR_TIME = 5

# sort branch csv based on commit start time
branches.sort(key=lambda x: x[COMMIT_START])

# sort commits csv based on time of commit time
commits.sort(key=lambda x: x[COMMIT_TIME])

# first commit - time to start at! last commit - time te stop!
start = datetime.strptime(commits[0][COMMIT_TIME], "%Y-%m-%d %H:%M:%S")
end = datetime.strptime(commits[len(commits) - 1][COMMIT_TIME], "%Y-%m-%d %H:%M:%S")

start = (start - timedelta(minutes=start.minute % 5)).replace(second=0)

totalMin = int(5 * round(float((end - start).days * 24 * 60)/5))
time_dic = {start + timedelta(minutes=x): 0 for x in range(0,totalMin,5)}

for branch in branches:
	commit_s = (datetime.strptime(branch[COMMIT_START], "%Y-%m-%d %H:%M:%S")).replace(second=0)
	commit_e = (datetime.strptime(branch[COMMIT_END], "%Y-%m-%d %H:%M:%S")).replace(second=0)

	commit_s = timedelta(minutes=commit_s.minute%5)
    t -= commit_s
    if commit_s > timedelta(0):
        t += timedelta(minutes=5)
        
	#while commit_s <= commit_e:

#csv = open(args.branchcsv[:-4] + "-window.csv", 'w')
#csv.write('time,num branches\n')
#Write out results
#for key in sorted(time_dic.keys()):
#	csv.write(str(time_dic[key]) + ',' + str(time_dic[key]))
#csv.close()


'''
print "from " + str(start) + " to " + str(end)
activity = []
point = start
while (point <= end):
	print "checking at point: " + str(point)
	numActiveBranches = 0

	for branch in branches:
		commit_s = datetime.strptime(branch[COMMIT_START], "%Y-%m-%d %H:%M:%S")
		commit_e = datetime.strptime(branch[COMMIT_END], "%Y-%m-%d %H:%M:%S")

		# if the commit time is in between
		if (commit_s > point):
			break;
		elif (point <= commit_e):
			numActiveBranches += 1

	activity.append([point, numActiveBranches])

	point = point + timedelta(hours=1)

csv = open(args.branchcsv[:-4] + "-window.csv", 'w')
csv.write('time,num branches\n')
for p in activity:
	line = str(p[0]) + ',' + str(p[1]) + '\n'
	csv.write(line)
csv.close()
'''
