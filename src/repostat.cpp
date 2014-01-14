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

	// Create directory to store repositories
	if ( ! S_ISDIR(st.st_mode) && mkdir(REPOS_DIR, 0755) < 0) {
		perror("Error creating repository directory");
		return 0;
	}

	git_repository *repo = NULL;
	const char *url  = "https://github.com/octocat/Spoon-Knife";
	const char *path = "repos/spoon";

	// Clone repository and open it. `git_clone` _does_ open it for us, but if
	// it fails (i.e. the repo exists) it wont open it. There's no harm in
	// re-opening the repo after cloning.
	git_clone(&repo, url, path, NULL);
	git_repository_open(&repo, path);

	git_revwalk *walker;

	// Setup revision walker to traverse the git repository directed graph of
	// commits in topological order. This will ensure we traverse through all
	// commits including merges
	git_revwalk_new(&walker, repo); // Returns Error Code
	git_revwalk_push_head(walker);  // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TOPOLOGICAL);

	git_oid oid1;
	git_oid oid2;
	git_commit *commit1;
	git_commit *commit2;
	git_tree *tree1;
	git_tree *tree2;
	git_diff *diff;
	git_patch *patch;

	// Grab the first object ID
	git_revwalk_next(&oid1, walker);

	// Iterate over every commit. Currently this will miss the last commit
	while ( ! git_revwalk_next(&oid2, walker)) {

		// Lookup this commit and the parent
		git_commit_lookup(&commit1, repo, &oid1);
		git_commit_lookup(&commit2, repo, &oid2);

		// Lookup the tree for each commit
		git_commit_tree(&tree1, commit1);
		git_commit_tree(&tree2, commit2);

		// Do a diff between the two trees and create a patch
		git_diff_tree_to_tree(&diff, repo, tree1, tree2, NULL);
		git_patch_from_diff(&patch, diff, 0);

		std::cerr << "COMMIT " << git_oid_allocfmt(&oid1) << '\n';

		// Move to the next object ID
		oid1 = oid2;
	}
	
	// Clean up memory
	git_revwalk_free(walker);
	git_repository_free(repo);

	return 0;
}
