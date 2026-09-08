---
marp: true
theme: gaia
paginate: true
---

<style>
  :root {
    /* Slide background, code foreground
       Second color is used for class: invert */
    --color-background: light-dark(#f9f9f9, #0288d1);
  }
</style>

# git Basics
<!-- _class: lead -->

Distributed version control

---

## Activity: Getting Started

<!-- _class: invert -->

1. Log in with an account at [github.com](https://github.com)

2. Visit https://github.com/thedataincubator/devsecops

3. Click _Fork_ button in top left

4. Check options; click _Create fork_

5. Let Github ponder this for a while, until it shows your fork

6. Click _Code_ ❭ _Codespaces_ ❭ &#xFF0B; to create new Codespace

It will take several minutes to launch your code space

---

## Version Control Systems (VCS)

Keep track of history of code
- Determine when and why (hopefully) change was made
- Understand when vulnerability or bug introduced
- Roll back to previous states

---

## Version Control Enables Collaboration

Shared state of system

Mechanism to exchange changes

Tools to resolve conflicting changes

---

## Early VCS: Client/Server

![bg right:40% fit](images/Client-server.svg)

- Server contains official state of project
- All users check out, check in with central server
- Merges difficult; generally avoided
- _RCS_, _CVS_, _Subversion_

---

## Distributed VCS (DVCS)

![bg right:40% fit](images/Distributed.svg)

- All users have full history
- Any user can exchange data with any other user
- "Official" version is a social construct
- Early 2000s: _BitKeeper_, _Mercurial_, _bazaar_, _Fossil_
- _git_ developed by Linus Torvalds, wins most mindshare

---

## DVCS in Practice

![bg right:40% fit](images/Distributed-practice.svg)

- One user is treated as official
- All other users pull and push changes to that one user
- Role often filled by _Github_, _Gitlab_
  - Generally provide other DevOps tooling

---

## Codespaces Overview

Virtual development machines running on Github servers

Interface based on VSCode

Machine configured according to `.devcontainer` folder

Can create multiple codespaces per repo

Codespaces shutdown after 30 minutes; restart quickly with preserved filesystem state

---

## Codespaces Quotas

Monthly quota for free GitHub accounts:

**Compute:** 120 CPU-hours
- Default machine has 2 CPUs
- Only charged while Codespace running

**Storage:** 15 GB-months
- Based on storage used in each Codespace
- Usage accrues for running or stopped Codespaces

---

## Managing Codespaces

View and manage your Codespaces at [github.com/codespaces](https://github.com/codespaces)

Track your usage at [github.com/settings/billing](https://github.com/settings/billing)

___Suggestions:___
- _Run only one Codespace at a time_
- _Delete Codespace if you don't plan to use it for some time_
  - _We'll talk about what to do to preserve configuration_

---

## VSCode AI Suggestions

If you don't want them:
- ☰ ❭ _File_ ❭ _Preferences_ ❭ _Settings_
- Three tiers of settings
  - _User:_ All Codespaces you open
  - _Remote:_ This particular Codespace
  - _Workspace:_ This particular repo
- Search for "Inline Suggest: Enabled"
  - Toggle off

<!--
The Workspace settings are stored in `.vscode`; they can be committed to the repo.
-->

---

## Getting Around git

We'll be primarily using the command line interface
- Always available
- Always capable

Many graphical interfaces, including in VSCode
- Interface to same operations
- Use them if you like!

---

## Initializing a git Repo

<pre><code
>git init <i>directory</i>
</code></pre>

Creates hidden `.git` folder in _`directory`_

git will use this directory to track the state and history of this repository

<!--
cd up to /workspaces, run git init there
Poke around .git a little bit
-->

---

## Current Status

```bash
git status
```

Shows current branch, current state

An alias I use often:

```bash
alias gits="git status"
```

---

## git's Two-Stage Commit Process

```bash
git add file.txt
```

Adds changes to the **staging area**
$\Rightarrow$ Lets us prep changes from several files into a single commit

```bash
git commit
```

Saves all changes in the staging area

Prompts for commit message
Here, VSCode; generally terminal text editor (_vi_, _nano_)

<!--
Edit file.txt (in nano probably)
git status => untracked file
Add to staging
git status => staged
commit
-->

---

## Good Commit Messages

Commit message should say _what_ and _why_, not _how_

```
Short summary of the changes in this commit

This is followed by one or more paragraphs describing what was done
and why this change was made.  We don't need to go into details of how
we accomplished the change; we can derive that from the git history.

Old timers (like me) try to keep the first line shorter than 60
characters.  The paragraphs should be hard-wrapped at 72 characters.
This helps the commit messages look good in various tools.
```

---

## Good Commit Messages

- First lines often written in "imperative" mood
  _Add new file_, not _Adds new file_
  - This matches style of automatic merge commits
- Start with capital letter
- No period at end of first line
- Some teams add commit **type** or **scope** to beginning
  - Types include feature, bugfix, docs, _etc._
  - Scope indicates portion of project affected

<!--
Commit message first line: When applied, this commit will...

Now, make additional edits, go through add and commit cycle again
-->

---

## Opinions on the Staging Area

- Some dislike the extra steps
  ```bash
  git commit -a
  ```
  Commits all _tracked_ files.

- Some like the ability to construct logical commits
  ```bash
  git add -p file.txt
  ```
  Lets you add individual "chunks" of a file
  $\Rightarrow$ Split mixed ideas into two commits

---

## Examining History

See past commits: `git log`

Compact log: `alias gl="git log --all --decorate --oneline --graph"`

Compare commits: `git diff id1 id2`
- Identifiers can be
  - hashes
  - branch names
  - `HEAD` for current commit
  - `HEAD^` for parent of current commit

---

## Branches

Branches allow switching between several versions

- Create a new branch: `git checkout -b my-branch`

- List all branches: `git branch`

- Switch current branch: `git checkout this-branch`

Switching branches changes the contents of the _working directory_, but all history is saved in `.git` folder

<!--
Create a new branch
Add and commit a new file
Switch to main, show that file disappears
Switch back to new branch; file is restored
-->

---

## Default Branch: _main_ or _master_

The default branch used to be called _master_

Recently, orgs have been shifting to calling it _main_

The names don't matter to git

<small>You can type _ma<tab>_ in either case!</small>

---

## Merging

```
git merge other-branch
```
Brings all changes committed to _other-branch_ into the current branch

If there are no **conflicts**, completes automatically

---

## Merge Conflicts

If both branches have changes in the same areas, git doesn't know which to keep.  It makes you figure it out.

```
This line is in both branches
<<<<<<< HEAD
This line is in the current branch
=======
This line is the incoming branch
>>>>>>> branch
```

You must edit the file to resolve the confict

Then, add and commit

<!--
Create conflict
Demo merge conflict both in file
and in VSCode (open with `code filename`; note that it will complain)

Resolve and commit
-->

---

## git-flow Strategy

<!-- _footer: Diagram by [Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/) -->

![bg right:50% fit](images/git-flow.png)

- _main_ branch for published
- _develop_ for primary work
- _release_ branches to prep for release into _main_
- _feature_ and _hotfix_ branches

From Vincent Driessen (2010)

Not for agile development

---

## Trunk-Based Development

<!-- _footer: Diagram from [dev.to](https://dev.to/arbitrarybytes/comparing-git-branching-strategies-dl4) -->

![bg right:35% fit](images/trunk.webp)

- _main_ keeps up with development
- Short lived _feature_ or _bugfix_ branches
  - Merged into _main_ once passing tests
- _main_ should always be passing CI
  - Able to deploy after any merge

Most DevOps teams use a pattern similar to this

<!--
After discussing:
Switch back to the main repo
Poke around a bit
-->

---

## Activity: Editing README

<!-- _class: invert -->

1. Create a new branch named _readme-link_

2. Add this line to the beginning of README.md
   ```
   [Launch Codespaces](https://codespaces.new/username/devsecops?quickstart=1)
   ```
   Replace `username` with your Github username

3. Commit the changes

---

## Copying Repos

![bg right:40% fit](images/fork-clone.svg)

**Fork:** Make a copy of a repo on the same host

**Clone:** Make a local copy of a repo
```bash
git clone repository-location
```
Access via
- SSH: Requires public key on host
- HTTPS: Sign in with password

---

## git Remotes

**Remotes** are other repos that your repo knows about

```bash
git remote              # Lists names
git remote -v           # Shows connection string
git remote show origin  # Detailed information on branches
```

The source of a clone is conventionally named _origin_.

---

## Communicating with Remotes

`git fetch [remote]`&mdash;Find out what's new on the remote

`git checkout branch-name`&mdash;Creates local branch with same name that **tracks** remote branch (use `origin/branch-name` to be explicit)

`git pull`&mdash;Gather changes from the remote branch being tracked

`git push -u origin branch-name`&mdash;Create new branch on _origin_ and set up tracking (only needed first time)

`git push`&mdash;Send changes to the remote tracking branch

---

## Activity: Push to Github

<!-- _class: invert -->

1. Push your _readme-link_ branch to your _origin_

A notification should appear on the main Github page for your repo

---

## Pull Requests

A common approach to approving changes

1. Open PR, request reviewer
2. Get feedback from reviewer
3. Make changes to address comments
   - Usually additional commits to same branch
4. Merge when approved
   - CLI or web UI

Not part of git itself; popularized by GitHub

---

## Activity: Pull Request

<!-- _class: invert -->

1. Create a PR for your _readme-link_ branch

2. Approve the PR
   <small>(if it meets your standards)</small>

3. Merge the _readme-link_ branch into _main_, via the web UI

4. In your Codespace, checkout the _main_ branch

5. Pull changes to the _main_ branch

Your edits to the README should now be in _main_ locally

---

## Multiple Remotes

A repo can have multiple remotes

We will publish updates to _thedataincubator/devsecops_
$\Rightarrow$ Let's add that as another remote

```bash
git remote add upstream https://github.com/thedataincubator/devsecops.git
```

Name _upstream_ is arbitrary

```bash
git fetch upstream  # Gather info about branches in this remote
```

---

## Activity: Find the Secret Word

<!-- _class: invert -->

In the _thedataincubator/devsecops_ repository, there is a branch named _git-exercise_

This branch has the secret word of the day in `exercises/git/README.md`

Find out what it is!

---

## Feedback

<!-- _class: lead invert -->
![](images/session1-qr.png)

[form.typeform.com/to/czK6zf1y](https://form.typeform.com/to/czK6zf1y)

<!--
Form link
-->
