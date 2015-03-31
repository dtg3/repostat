for f in *.git
do
    filename="${f%.*}"
    echo "Process: $filename"
    mkdir -p "$filename/.git"
    mv $f/* "$filename/.git/"
    rm -rf $f
    ( cd "$filename" && git config --local --bool core.bare false && git reset --hard)
done