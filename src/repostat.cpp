#include <git2.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <time.h>
#include <libgen.h>

typedef struct diff_data
{
	public:
		char* diff_id;
		unsigned int line;
		unsigned int file;
		unsigned int hunk;
	~diff_data()
	{ 
    	if (diff_id) delete diff_id;
    }
} diff_data;

int each_file_cb(const git_diff_delta *delta, float progress, void *payload)
{
	diff_data *diffStats = (diff_data*)payload;
	diffStats->file = diffStats->file + 1;

	return 0;
}

int each_hunk_cb(const git_diff_delta *delta, const git_diff_hunk *hunk,
		void *payload)
{
	diff_data *diffStats = (diff_data*)payload;
	diffStats->hunk = diffStats->hunk + 1;

	return 0;
}

int each_line_cb(const git_diff_delta *delta, const git_diff_hunk *hunk,
		const git_diff_line *line, void *payload)
{
	diff_data *diffStats = (diff_data*)payload;

	if(line->origin == GIT_DIFF_LINE_ADDITION || line->origin == GIT_DIFF_LINE_DELETION)
		diffStats->line = diffStats->line + 1;

	return 0;
}

std::string filename(const char *repopath)
{
	// Obtain the base name of the provided path
	char* path = const_cast<char*>(repopath);
	std::stringstream filename;
	filename << "results/" << basename(path) << ".";

	// Append the current time to the end of the file name. Don't want to
	// accidently over-write old data...
	time_t t = time(0);
	struct tm *now = localtime(&t);

	filename << (now->tm_year + 1900) << "-"
	         << (now->tm_mon + 1)     << "-"
	         << (now->tm_mday)
	         << "."
	         << (now->tm_hour) << "-"
	         << (now->tm_min)  << "-"
	         << (now->tm_sec)
	         << ".csv";

	return filename.str();
}

void writeToCSV(std::ofstream& output, const diff_data& diffStats) {
	// Create unique output file to place resulting repository history
	output << diffStats.diff_id << ", "
	       << diffStats.file << ", "
		   << diffStats.hunk << ", "
		   << diffStats.line << "\n";

}

void outputToTerminal(const diff_data& diffStats) {
	std::cout << "Commit ID: " << diffStats.diff_id << "\n"
			  << "Files: " << diffStats.file << "\n"
			  << "Hunks: " << diffStats.hunk << "\n"
			  << "Lines: " << diffStats.line << "\n"
			  << "--------------------------------------\n";
}

int main(int argc, char *argv[])
{
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
	git_revwalk_push_head(walker);  // Returns Error Code
	git_revwalk_sorting(walker, GIT_SORT_TOPOLOGICAL);

	git_oid oid1;
	git_oid oid2;
	git_commit *commit1;
	git_commit *commit2;
	git_tree *tree1;
	git_tree *tree2;
	git_diff *diff;

	// Grab the first object ID
	git_revwalk_next(&oid1, walker);

	std::ofstream output( filename(path).c_str() );
	output << "sha, files modified, hunks modified, lines modified\n";

	// Iterate over every commit. Currently this will miss the first commit
	while ( ! git_revwalk_next(&oid2, walker))
	{
		// Seup the struct for the data we care about
		diff_data diffStats = {};

		diffStats.diff_id = git_oid_allocfmt(&oid1);

		// Lookup this commit and the parent
		git_commit_lookup(&commit1, repo, &oid1);
		git_commit_lookup(&commit2, repo, &oid2);

		// Lookup the tree for each commit
		git_commit_tree(&tree1, commit1);
		git_commit_tree(&tree2, commit2);

		// Do a diff between the two trees and create a patch
		git_diff_tree_to_tree(&diff, repo, tree1, tree2, NULL);

		// Iterate through each delta within the diff to get file, line, and
		// hunk info.  Note that this does not skip over merge commits, but
		// it's not gauraunteed to return the correct information for certain
		// merge commits.
		if ( ! git_diff_foreach(diff, each_file_cb, each_hunk_cb, each_line_cb, &diffStats))
		{
			writeToCSV(output, diffStats);
			//outputToTerminal(diffStats);
		}
		else
		{
			std::cerr << "Diff Error!\n";
		}

		// Move to the next object ID
		oid1 = oid2;

		// Clean up memory
		git_commit_free(commit1);
		git_commit_free(commit2);
		git_tree_free(tree1);
		git_tree_free(tree2);
		git_diff_free(diff);
	}

	// Clean up memory
	git_revwalk_free(walker);
	git_repository_free(repo);

	return 0;
}
