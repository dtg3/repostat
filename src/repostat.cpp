#include <git2.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>

#include <iostream>

int main(int argc, char * argv[]) {

	// Create directory to store repos
	if (mkdir("repos", 0755) != 0) {
		perror("Error creating repository directory");
		return 0;
	}

	git_repository *repo = NULL;
	const char *url = "https://github.com/octocat/Spoon-Knife";
	const char *path = "repos/spoon";

	// Check if repo is already cloned
	if (git_clone(&repo, url, path, NULL) == GIT_EEXISTS) {
		git_repository_open(&repo, path);
	}

	git_revwalk *walker;

	git_revwalk_new(&walker, repo); // Returns Error Code
	git_revwalk_push_head(walker); // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TIME | GIT_SORT_REVERSE);

	git_oid oid;
	int i = 0;
	while (!git_revwalk_next(&oid, walker)) {
		std::cerr << "REV# " << ++i << "\n";
	}
	
	git_revwalk_free(walker);
	git_repository_free(repo);
	return 0;
}
