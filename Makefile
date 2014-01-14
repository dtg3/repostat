bin/repostat: src/repostat.cpp
	mkdir -p bin
	g++ src/repostat.cpp -Wall -std=c++11 -lgit2 -o bin/repostat

.PHONY: clean
clean:
	rm -rf bin/repostat
