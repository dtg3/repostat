echo "ALL BRANCHES"
for f in ./data/all-branches/*-branch.csv;
do
    echo "Running: $f"
    python window.py $f --minutes=5
done

echo "ONLY MASTER"
for f in ./data/only-master/*-branch.csv;
do 
    echo "Running: $f"
    python window.py $f --minutes=5
done
