for dir in *
do
    echo "process $dir"
    (cd "$dir" && find . -type f -not -path "./.git*" -print0 | xargs -0 cat | wc -l)
done