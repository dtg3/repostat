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

	git_revwalk_new(&walker, repo); // Returns Error Code
	git_revwalk_push_head(walker); // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TOPOLOGICAL);

	git_oid oid1;
	git_oid oid2;
	git_commit *commit1;
	git_commit *commit2;
	git_tree *tree1;
	git_tree *tree2;
	git_diff *diff;
	git_patch *patch;

	// Pop the very first commit
	git_revwalk_next(&oid1, walker);

	while ( ! git_revwalk_next(&oid2, walker)) {
		// Lookup this commit and the parent
		git_commit_lookup(&commit1, repo, &oid1);
		git_commit_lookup(&commit2, repo, &oid2);

		// Lookup the tree for each commit
		git_commit_tree(&tree1, commit1);
		git_commit_tree(&tree2, commit2);

		// Do diff between the two trees and create a patch
		git_diff_tree_to_tree(&diff, repo, tree1, tree2, NULL);
		git_patch_from_diff(&patch, diff, 0);

		std::cerr << "REV# " << git_oid_allocfmt(&oid1) << '\n';

		oid1 = oid2;
	}
	
	git_revwalk_free(walker);
	git_repository_free(repo);
	return 0;
}
