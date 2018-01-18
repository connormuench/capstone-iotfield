# README

Instructions for the various components of the project can be found in README files in each directory.

## General Commit Policy

Individual components may have additional commit policies, specified within their README files. This policy applies to all commits in the repository.

### Commit Messages

All commits must have messages. Add all modified files with `git add -A` and commit the changes with `git commit -m "<your message here>"`.

### Commit Frequency

Pushing every commit to GitHub immediately isn't necessary, but local commits should be done after any substantial changes or additions as well as immediately before a push. Use your best judgment when determining when to make a commit. The repository shouldn't be drowning in individual commits, or else finding a particular commit will be needlessly difficult. At the same time, if a commit is reverted, we don't want to lose too much unrelated progress.

### Testing

The Rails test suites must be run prior to a push with intent to open a pull request, as TravisCI will fail the pull request if the test suites fail. Run them with `rails t` from within the `webapp` directory.

## Common commands

`git clone https://github.com/connormuench/capstone-iotfield.git`: Clones the repository to the current working directory. It will also set the `origin` remote to the GitHub URL automatically. This only fetches the `master` branch.

`git fetch origin <branch name>`: Fetches the specified branch from the remote repository.

`git checkout <branch name>`: Switches to the specified branch. If it is a remote branch, make sure to `fetch` it first.

`git checkout -b <branch name>`: Creates a new branch with the specified name and switches to it.

`git status`: Shows information about the state of the local repository, like current branch, untracked files, and so on.

`git add -A`: Forces all untracked files in the local repository to be tracked. Useful after adding or removing several files.

`git commit -m "<your message here>"`: Commits tracked changes to the local repository.

`git pull origin <branch name>`: Fetches the specified branch from the remote repository and merges it to the current local checkout. Prior to pushing with the intent to open a pull request on the current branch, always run this command with `<branch name>` as `master` to ensure there are no merge conflicts with the master branch.

`git push origin <branch name>`: Pushes and merges the current checkout to the specified remote branch. `<branch name>` will almost always just be the name of the currently checked out branch.
