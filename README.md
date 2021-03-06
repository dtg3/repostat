repostat
========

Tool for collecting various information about git source code repositories.

#### Per Commit Metrics

 * No. of lines of code modified (additions + deletions)
 * No. of hunks modified
 * No. of files modified
 * No. of methods modified
 * Is it a merge?


#### Time Metrics: Per hour, day, week, month, quarter, year, lifespan

 * No. commits
 * No. specific commit metrics (see above)
 * No. contributors (commit authors)
 * No. branches


These statistics are intended to answer a set of queries, such as
 * During what time periods is the project most active?
 * When are lines, hunks, files, or methods modified most closely correlated?


#### Usage:

##### `repostat [repo-path]`

Goes through the history of the provided repository and calculates the total number of line changes, hunks, and files
modified for each commit SHA. Stores the data in a CSV file, uniquely named
results/repo-path-results.yyyy-mm-dd.hh-mm-ss.csv, with the appropriate time used.
