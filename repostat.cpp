#include <boost/filesystem.hpp>
#include <git2.h>

// g++ repostat.cpp -lboost_filesystem -lboost_system -lgit2 -o rs
int main(int argc, char * argv[]) {
	if (boost::filesystem::create_directory("repos"))
		std::cerr << "Done!\n";

	git_repository *repo = NULL;
	const char *url = "https://github.com/octocat/Spoon-Knife";
	const char *path = "repos/spoon";
	int error = git_clone(&repo, url, path, NULL);
	// Check for error

	git_revwalk *walker;

	error = git_revwalk_new(&walker, repo);
	error = git_revwalk_push_head(walker);
	git_revwalk_sorting(walker, GIT_SORT_TIME | GIT_SORT_REVERSE);

	git_oid oid;
	int i = 0;
	while (!git_revwalk_next(&oid, walker)) {
		std::cerr << "REV# " << ++i << "\n";
	}
}