bin/repostat: src/repostat.cpp
	mkdir -p bin
	g++ src/repostat.cpp -Wall -I/usr/local/include -L/usr/local/lib -lgit2 -o bin/repostat

.PHONY: clean
clean:
	rm -rf bin/repostat
