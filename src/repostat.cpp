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

typedef struct diff_data
{
	char* diff_id;
	unsigned int line;
	unsigned int lineAdded;
	unsigned int lineRemoved;
	unsigned int file;
	unsigned int hunk;
	unsigned int parents;

	#ifdef __APPLE__
	~diff_data()		
	{ 		
		if (diff_id) free(diff_id);		
	}
	#endif

} diff_data;

typedef struct commit_data
{
	git_time_t time;
	int timeOffset;
	unsigned int numParents;
	char* author;
	char* committer;
	const char* msg;
} commit_data;

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
	bool whiteSpaceOnly = true;

	diff_data *diffStats = (diff_data*)payload;

	for (size_t i = 0; i < line->content_len; ++i) {
		//if (diffStats->parents > 1)
			//std::cout << line->content[i];
		
		// Check for common whitespace
		if (line->content[i] == '\n')
			continue;

		if (line->content[i] == '\t')
			continue;

		if (line->content[i] == ' ')
			continue;

		// If there is a non whitespace character we
		//   want to consider the line;
		whiteSpaceOnly = false;

		//if (diffStats->parents <= 1)
		break;
	}

	if(!whiteSpaceOnly && (line->origin == GIT_DIFF_LINE_ADDITION || line->origin == GIT_DIFF_LINE_DELETION)) {
		++(diffStats->line);
		if (line->origin == GIT_DIFF_LINE_DELETION) {
			++(diffStats->lineAdded);
		}
		if (line->origin == GIT_DIFF_LINE_ADDITION) {
			++(diffStats->lineRemoved);
		}
	}

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

std::string convertTime(git_time_t t)
{
	time_t tm(t);
	char ct[] = "YYYY-MM-DDThh:mm:ssZ";
	strftime(ct, sizeof ct, "%FT%TZ", gmtime(&tm));

	std::string stime = std::string(ct);
	return stime;
}

void writeToCSV(std::ofstream& output, const diff_data& diffStats, 
		const commit_data& commitStats)
{
	output << diffStats.diff_id << ";"
	       << diffStats.file << ";"
	       << diffStats.hunk << ";"
	       << diffStats.lineAdded << ";"
	       << diffStats.lineRemoved << ";"
	       << diffStats.line << ";"
	       << convertTime(commitStats.time) << ";"
	       << commitStats.timeOffset << ";"
	       << commitStats.numParents << ";"
	       << commitStats.author << ";"
	       << commitStats.committer << ";"
	       << commitStats.msg << "\n";
}

void outputToTerminal(const diff_data& diffStats, const commit_data& commitStats)
{
	std::cout << "Commit ID: " << diffStats.diff_id << "\n"
	          << "Files: " << diffStats.file << "\n"
	          << "Hunks: " << diffStats.hunk << "\n"
	          << "Lines Added: " << diffStats.lineAdded << "\n"
	          << "Lines Removed: " << diffStats.lineRemoved << "\n"
	          << "Total Lines: " << diffStats.line << "\n"
	          << "Time: " << convertTime(commitStats.time) << "\n"
	          << "Time Offset:" << commitStats.timeOffset << "\n"
	          << "Parents: " << commitStats.numParents << "\n"
	          << "Author: " << commitStats.author << "\n"
	          << "Committer: " << commitStats.committer << "\n"
	          << "Message: " << commitStats.msg << "\n"
	          << "--------------------------------------\n";
}

void progressBarUpdate()
{
	// Viewable only when we're not already outputting to the terminal
	static long int count = 0;
	std::cout << "Total commits analyzed: " << ++count << "\r";
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

	git_oid oid;
	git_commit *commit;
	git_commit *parent;
	git_tree *commit_tree;
	git_tree *parent_tree;
	git_diff *diff;
	git_diff_options opts = GIT_DIFF_OPTIONS_INIT;

	// Set Diff Flag Options
	opts.flags |= GIT_DIFF_IGNORE_WHITESPACE;
	opts.flags |= GIT_DIFF_IGNORE_WHITESPACE_CHANGE;
	opts.flags |= GIT_DIFF_IGNORE_WHITESPACE_EOL;
	// opts.flags |= GIT_DIFF_MINIMAL;

	// Turn off context to only get modified lines
	opts.context_lines = 0;

	// Create unique output file to place resulting repository history
	std::ofstream output( filename(path).c_str() );

	if ( ! output)
	{
		std::cerr << "Could not open output folder at: " << filename(path) << "\n";
		return 2;
	}

	// CSV headers
	output << "sha;files modified;hunks modified;lines added;lines removed;lines modified;"
	       << "commit time;offset;number of parents;author;committer;message\n";

	// Iterate over every commit. Currently this will miss the first commit
	while ( ! git_revwalk_next(&oid, walker))
	{
		// Seup the structs for the data we care about
		diff_data diffStats = {};
		commit_data commitStats = {};

		#ifdef __APPLE__
			diffStats.diff_id = git_oid_allocfmt(&oid);
		#else
			diffStats.diff_id = git_oid_tostr_s(&oid);
		#endif

		// Lookup this commit
		git_commit_lookup(&commit, repo, &oid);
		git_commit_tree(&commit_tree, commit);

		// Get commit specific data
		commitStats.time       = git_commit_time(commit);
		commitStats.timeOffset = git_commit_time_offset(commit);
		commitStats.numParents = git_commit_parentcount(commit);
		commitStats.author     = git_commit_author(commit)->name;
		commitStats.committer  = git_commit_committer(commit)->name;
		diffStats.parents      = commitStats.numParents;

		// Replace new lines, quotes, and semicolons from commit message for storage
		std::string sMessage = std::string(git_commit_message(commit));
		std::replace( sMessage.begin(), sMessage.end(), '\n', ' ');
		std::replace( sMessage.begin(), sMessage.end(), ';', '-');
		std::replace( sMessage.begin(), sMessage.end(), '\"', '\'');
		commitStats.msg = sMessage.c_str();

		git_commit_parent(&parent, commit, 0);
		git_commit_tree(&parent_tree, parent);

		// Do a diff between the two trees and create a patch
		git_diff_tree_to_tree(&diff, repo, commit_tree, parent_tree, &opts);
		// Iterate through each delta within the diff to get file, line, and
	
		// hunk info.  Note that this does not skip over merge commits, but
		// it's not gauraunteed to return the correct information for certain
		// merge commits.
		if (git_diff_foreach(diff, each_file_cb, each_hunk_cb, each_line_cb, &diffStats))
			std::cerr << "\nDiff error on sha: " << diffStats.diff_id << "!\n";

		writeToCSV(output, diffStats, commitStats);
		//outputToTerminal(diffStats, commitStats);

		// Update Progress
		progressBarUpdate();

		// Clean up memory
		git_commit_free(commit);
		git_tree_free(commit_tree);
		git_commit_free(parent);
		git_tree_free(parent_tree);
		git_diff_free(diff);
	}

	// Clean up memory
	git_revwalk_free(walker);
	git_repository_free(repo);

	// Move output to new terminal line
	std::cout << "\n";
	
	return 0;
}
