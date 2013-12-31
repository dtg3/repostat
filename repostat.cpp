#include <boost/filesystem.hpp>
#include <git2.h>

// g++ repostat.cpp -lboost_filesystem -lboost_system -llibgit2 -o rs
int main(int argc, char * argv[]) {
	if (boost::filesystem::create_directory("repos"))
		std::cerr << "Done!\n";

	git_repository *repo = NULL;
	const char *url = "https://github.com/octocat/Spoon-Knife";
	const char *path = "repos";
	int error = git_clone(&repo, url, path, NULL);
}