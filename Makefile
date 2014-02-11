bin/repostat: src/repostat.cpp
	mkdir -p bin
	g++ src/repostat.cpp -Wall -lgit2 -o bin/repostat

.PHONY: clean
clean:
	rm -rf bin/repostat
