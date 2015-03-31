
for f in ../github-repos/*.git;
do
    echo "Running: $f"
    #echo "File:"
    #git --git-dir $f ls-tree -r master --name-only | wc -l
    #echo "Commits:"
    #git --git-dir $f rev-list --all | wc -l
    #echo "Last Commit:"
    #git --git-dir $f log -1
    echo "LOC:"
    for file in $(git --git-dir $f ls-tree --name-only -r HEAD); do
	git show HEAD:"$file"
    done | wc -l
done