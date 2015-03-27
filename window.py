
import csv
import argparse
from operator import itemgetter
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument('branchcsv')
parser.add_argument('-m', '--minutes', type=int)

#parser.add_argument('commitcsv')

args = parser.parse_args()

with open(args.branchcsv, 'rb') as fbranch:
    breader = csv.reader(fbranch)
    branches = list(breader)
    branches.pop(0) # get rid of header

#with open(args.commitcsv, 'rb') as fcommits:
#    creader = csv.reader(fcommits)
#    commits = list(creader)
#    commits.pop(0) # get rid of header


# index into branch csv file
BRANCH_ID = 0
COMMIT_START = 16
COMMIT_END = 17
COMMIT_WINDOW = 18
AUTHOR_START = 19
AUTHOR_END = 20
AUTHOR_WINDOW = 21

# index into commit csv file
#COMMIT_TIME = 4
#AUTHOR_TIME = 5

# INEFFICIENT I KNOW!!!!
# sort branch csv based on commit start time
branches.sort(key=lambda x: x[COMMIT_END])
end = datetime.strptime(branches[len(branches) - 1][COMMIT_END], "%Y-%m-%d %H:%M:%S")
branches.sort(key=lambda x: x[COMMIT_START])
start = datetime.strptime(branches[0][COMMIT_START], "%Y-%m-%d %H:%M:%S")

# sort commits csv based on time of commit time
#commits.sort(key=lambda x: x[COMMIT_TIME])

# first commit - time to start at! last commit - time te stop!
#start = datetime.strptime(commits[0][COMMIT_TIME], "%Y-%m-%d %H:%M:%S")
#end = datetime.strptime(commits[len(commits) - 1][COMMIT_TIME], "%Y-%m-%d %H:%M:%S")

SET_RANGE = 5

if args.minutes:
	if (args.minutes > 60):
		args.minutes = 60
		
	SET_RANGE = args.minutes

# Slide the starting time window 5 minutes before the first commit (just ensures we have a starting window)
start = (start - timedelta(minutes=start.minute % SET_RANGE)).replace(second=0)
start -= timedelta(minutes=SET_RANGE)

totalMin = int(SET_RANGE * round(float(((end - start).total_seconds())/60)/SET_RANGE)) + SET_RANGE
time_dic = {start + timedelta(minutes=x): 0 for x in range(0,totalMin,SET_RANGE)}

for branch in branches:
	commit_s = (datetime.strptime(branch[COMMIT_START], "%Y-%m-%d %H:%M:%S")).replace(second=0)
	commit_e = (datetime.strptime(branch[COMMIT_END], "%Y-%m-%d %H:%M:%S")).replace(second=0)

	while commit_s <= commit_e:
		point = commit_s
		discard = timedelta(minutes=commit_s.minute % SET_RANGE)
		point -= discard

		if discard >= timedelta(minutes= (SET_RANGE / float(2))):
			point += timedelta(minutes=SET_RANGE)

		if point in time_dic:
			time_dic[point] += 1
		else:
			print "uh oh - " + str(point) + " " + branch[BRANCH_ID]

		commit_s += timedelta(minutes=SET_RANGE)

#print('time,num branches')
#for key in sorted(time_dic.keys()):
	#print str(key) + "," + str(time_dic[key])

csv = open(args.branchcsv[:-4] + "-window.csv", 'w')
csv.write('time,num branches\n')

#Write out results
for key in sorted(time_dic.keys()):
	csv.write(str(key) + ',' + str(time_dic[key]) + '\n')

csv.close()
