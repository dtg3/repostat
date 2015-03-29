
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('branchcsv')
parser.add_argument('mastercsv')

#parser.add_argument('commitcsv')

args = parser.parse_args()

with open(args.branchcsv, 'rb') as fbranch:
    breader = csv.reader(fbranch)
    branches = list(breader)
    branches.pop(0) # get rid of header

with open(args.mastercsv, 'rb') as mbranch:
    mreader = csv.reader(mbranch)
    master = list(mreader)
    master.pop(0) # get rid of header

# index into branch csv file
BRANCH_ID = 0

masterDict = {}

# Output
f = open(args.branchcsv[:-4] + "-diff.csv", 'w')
out = csv.writer(f)
f.write('id,num commits,branch files,avg branch files pc,commit files,avg commit files pc,branch locs added, branch locs removed,branch locs total,avg branch locs total pc,commit locs added, commit locs removed,commit locs total,avg commit locs total pc,branch hunks,avg branch hunks pc,commit hunks,avg commit hunks pc,num unique authors,num unique committers,commit start time,commit end time,commit time window,author start time, author end time,author time window\n')

print "Build Branches"

for linear in master:
	masterDict[linear[BRANCH_ID]] = linear

print "Diffing Results"
for blinear in branches:
	if blinear[BRANCH_ID] not in masterDict:
		out.writerow(blinear)

f.close()
