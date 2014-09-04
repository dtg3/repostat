for file in data/*
do
   touch results/$(basename $file).txt
   { time ./bin/repostat $file ; } 2> results/$(basename $file).txt
done