#!bin/bash

FILES="../../collected-repos/git-repos/Faker.git
../../collected-repos/git-repos/angular.js.git
../../collected-repos/git-repos/bootstrap.git
../../collected-repos/git-repos/brackets.git
../../collected-repos/git-repos/d3.git
../../collected-repos/git-repos/django.git
../../collected-repos/git-repos/git.git
../../collected-repos/git-repos/gitignore.git
../../collected-repos/git-repos/gitlabhq.git
../../collected-repos/git-repos/homebrew.git
../../collected-repos/git-repos/html5-boilerplate.git
../../collected-repos/git-repos/impress.js.git
../../collected-repos/git-repos/jquery.git
../../collected-repos/git-repos/libgit2.git
../../collected-repos/git-repos/meteor.git
../../collected-repos/git-repos/node.git
../../collected-repos/git-repos/oh-my-zsh.git
../../collected-repos/git-repos/rails.git
../../collected-repos/git-repos/mongo.git
../../collected-repos/git-repos/linux.git"


for f in $FILES
do
	name=$(echo $f | rev | cut -c 5- | rev)
	name="${name##*/}"
	echo "Processing $f with csv of $name"
	time python gitty.py "${f}" --csv "overnight/${name}"
done
