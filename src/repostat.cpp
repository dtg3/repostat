#include <git2.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include <iostream>

#define REPOS_DIR "repos"


int main(int argc, char * argv[]) {

	// Look for the repository directory
	struct stat st;
	stat(REPOS_DIR, &st);

	// Create directory to store repos
	if ( ! S_ISDIR(st.st_mode) && mkdir(REPOS_DIR, 0755) < 0) {
		perror("Error creating repository directory");
		return 0;
	}

	git_repository *repo = NULL;
	const char *url = "https://github.com/octocat/Spoon-Knife";
	const char *path = "repos/spoon";

	// Clone repo, and open it
	git_clone(&repo, url, path, NULL);
	git_repository_open(&repo, path);

	git_revwalk *walker;
	git_oid oid;

	git_revwalk_new(&walker, repo); // Returns Error Code
	git_revwalk_push_head(walker); // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TIME | GIT_SORT_REVERSE);

	while ( ! git_revwalk_next(&oid, walker)) {
		std::cerr << "REV# " << git_oid_allocfmt(&oid) << '\n';
	}
	
	git_revwalk_free(walker);
	git_repository_free(repo);
	return 0;
}
