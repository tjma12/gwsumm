# Contributing to GWSumm

This is [@alurban](//github.com/alurban)'s and [@duncanmmacleod](//github.com/duncanmmacleod/)'s workflow, which might work well for others. It is merely a verbose version of the [GitHub flow](https://guides.github.com/introduction/flow/).

The basic idea is to use the `master` branch of your fork as a way of updating your fork with other people's changes that have been merged into the main repo, and then  working on a dedicated _feature branch_ for each piece of work:

- create the fork (if needed) by clicking _Fork_ in the upper-right corner of https://github.com/gwpy/gwsumm/ - this only needs to be done once, ever
- clone the fork into a new folder dedicated for this piece of work (replace `<username>` with yout GitHub username):

  ```bash
  git clone https://github.com/<username>/gwsumm.git gwsumm-my-work  # change gwsumm-my-work as appropriate
  cd gwsumm-my-work
  ```
  
- link the fork to the upstream 'main' repo:

  ```bash
  git remote add upstream https://github.com/gwpy/gwsumm.git
  ```
  
- pull changes from the upstream 'main' repo onto your fork's master branch to pick up other people's changes, then push to your remote to update your fork on github.com

  ```bash
  git pull --rebase upstream master
  git push
  ```

- create a new branch on which to work

  ```bash
  git checkout -b my-new-branch
  ```
  
- make commits to that branch
- push changes to your remote on github.com

  ```bash
  git push -u origin my-new-branch
  ```

- open a merge request on github.com
- when the request is merged, you should 'delete the source branch' (there's a button), then just delete the clone of your fork and forget about it

 ```bash
  cd ../
  rm -rf ./gwsumm-my-work
  ```

And that's it.

 ## Coding guidelines

 ### Python compatibility

 **GWSumm code must be compatible with Python versions >=3.5.**

 ### Style

 This package follows [PEP 8](https://www.python.org/dev/peps/pep-0008/),
 and all code should adhere to that as far as is reasonable.

 The first stage in the automated testing of pull requests is a job that runs
 the [`flake8`](http://flake8.pycqa.org) linter, which checks the style of code
 in the repo. You can run this locally before committing changes via:

 ```bash
 python -m flake8
 ```

 ### Testing

 GWSumm has a relatively incomplete test suite, covering less than 40% of the codebase.
 All code contributions should be accompanied by (unit) tests to be executed with
 [`pytest`](https://docs.pytest.org/en/latest/), and should cover
 all new or modified lines.

 You can run the test suite locally from the root of the repository via:

 ```bash
 python -m pytest gwsumm/
 ```
