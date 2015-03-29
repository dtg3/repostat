for branch in ./data/all-branches/*-commit.csv;
do
    master="./data/only-master/${branch##*/}"
    echo "Running: $branch and $master"
    python branchdiff.py $branch $master
done