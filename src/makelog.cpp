
#include <iostream>
#include <fstream>

void progressBarUpdate()
{
	// Viewable only when we're not already outputting to the terminal
	static long int count = 0;
	std::cout << "Total commits analyzed: " << ++count << "\r";
}

int main()
{
	const int NUM_FILES = 23;
	std::string csvFiles[NUM_FILES] = {
		"../results/Font-Awesome.2014-3-10.22-15-40.csv",
		"../results/angular.js.2014-3-10.22-23-52.csv",
		"../results/bootstrap.2014-3-8.9-46-38.csv",
		"../results/d3.2014-4-2.11-7-1.csv",
		"../results/django.2014-3-10.14-19-3.csv",
		"../results/freebsd.2014-3-9.0-20-21.csv",
		"../results/gcc.2014-3-8.10-2-56.csv",
		"../results/git.2014-3-8.10-1-18.csv",
		"../results/homebrew.2014-3-9.22-1-49.csv",
		"../results/html5-boilerplate.2014-3-10.21-11-35.csv",
		"../results/impress.js.2014-3-10.22-13-53.csv",
		"../results/jquery.2014-3-10.21-7-29.csv",
		"../results/libgit2.2014-3-8.9-50-22.csv",
		"../results/linux.2014-3-6.14-32-50.csv",
		"../results/mongo.2014-3-8.8-49-13.csv",
		"../results/node.2014-3-8.12-58-54.csv",
		"../results/nova.2014-3-10.19-10-13.csv",
		"../results/opencv.2014-3-8.9-6-21.csv",
		"../results/rails.2014-3-10.9-30-25.csv",
		"../results/ruby.2014-3-8.9-27-19.csv",
		"../results/shogun.2014-3-8.9-39-34.csv",
		"../results/v8.2014-3-8.14-3-43.csv",
		"../results/xbmc.2014-3-9.19-16-51.csv" };

	std::string repos[NUM_FILES] = { 
		"Font-Awesome",
		"angular.js",
		"bootstrap",
		"d3",
		"django",
		"freebsd",
		"gcc",
		"git",
		"homebrew",
		"html5-boilerplate",
		"impress.js",
		"jquery",
		"libgit2",
		"linux",
		"mongo",
		"node",
		"nova",
		"opencv",
		"rails",
		"ruby",
		"shogun",
		"v8",
		"xbmc" };

	std::ofstream output("all.csv");

	output << "repository, "
	       << "sha, "
	       << "files modified, "
	       << "hunks modified, "
	       << "lines modified, "
	       << "commit time, "
	       << "number of parents, "
	       << "author, "
	       << "committer\n";

	for (int i = 0; i < NUM_FILES; ++i)
	{
		std::ifstream input(csvFiles[i]);
		std::string repo;
		repo = repos[i];

		// Ignore the first line (header)
		std::string temp;
		for (int i = 0; i < 8; ++i)
			std::getline(input, temp);

		if ( ! input)
		{
			std::cout << "\nCouldn't open file " << csvFiles[i] << "\n";
			return 1;
		}

		while ( ! input.eof())
		{
			std::string line;
			std::getline(input, line);
			output << repo << ", " << line << "\n";

			progressBarUpdate();
		}

		input.close();
	}

	std::cout << "\n";
	output.close();
	return 0;
}
