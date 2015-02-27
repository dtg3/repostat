/*
	@brief Collects metrics on the commit history of a repository
*/

#include "git2.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <time.h>
#include <libgen.h>
#include <ctime>
#include <algorithm>

int main(int argc, char *argv[])
{
	git_libgit2_init();

	if (argc < 2)
	{
		std::cerr << "Repository path required.\n";
		return 1;
	}

	const char *path = argv[1];
	git_repository *repo = NULL;
	git_repository_open(&repo, path);
	
	git_revwalk *walker;

	// Setup revision walker to traverse the git repository directed graph of
	// commits in topological order. This will ensure we traverse through all
	// commits including merges
	git_revwalk_new(&walker, repo); // Returns Error Code
	
	if (argc < 3) {
		git_revwalk_push_ref(walker, "refs/heads/master");
	}
	else {
		git_revwalk_push_ref(walker, ("refs/heads/" + std::string(argv[2])).c_str());
	}

	// git_revwalk_push_head(walker);  // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TOPOLOGICAL);

	git_oid oid;
	git_commit *commit;
	//git_commit *parent;
	//git_tree *commit_tree;
	//git_tree *parent_tree;

	// Iterate over every commit. Currently this will miss the first commit
	while ( ! git_revwalk_next(&oid, walker))
	{
		git_commit_lookup(&commit, repo, &oid);
		//git_commit_tree(&commit_tree, commit);

		// Get commit specific data
		std::cout << "COMMIT:\n";
		std::cout << git_commit_id(commit) << "\n";
		std::cout << git_commit_tree_id(commit) << "\n";
		std::cout << "-----------\n";
		std::cout << "PARENTS: " << git_commit_parentcount(commit) << "\n";
		std::cout << git_commit_time(commit) << "\n";
		std::cout << git_commit_time_offset(commit) << "\n";
		std::cout << git_commit_parentcount(commit) << "\n";
		std::cout << git_commit_author(commit)->name << "\n";
		std::cout << git_commit_committer(commit)->name << "\n";

		// Replace new lines, quotes, and semicolons from commit message for storage
		std::string sMessage = std::string(git_commit_message(commit));
		std::replace( sMessage.begin(), sMessage.end(), '\n', ' ');
		std::replace( sMessage.begin(), sMessage.end(), ';', '-');
		std::replace( sMessage.begin(), sMessage.end(), '\"', '\'');
		std::cout << sMessage.c_str() << "\n";

		//git_commit_parent(&parent, commit, 0);
		//git_commit_tree(&parent_tree, parent);

		// Clean up memory
		git_commit_free(commit);
		//git_tree_free(commit_tree);
		//git_commit_free(parent);
		//git_tree_free(parent_tree);
	}

	// Clean up memory
	git_revwalk_free(walker);
	git_repository_free(repo);
	
	git_libgit2_shutdown();

	return 0;
}
