## Asana view.

Simple display of asana stuff for team screens.

## Including:

- setup.sh (run this, and sets up everything). Can be run as often as you wish.
- autogenerates a basic SECRET KEY in the config.
- virtualenv 1.9.1 (in it's own .virtualenv folder, out of the way)
- pylint pre-commit hook (from Sebastian Dahlgren)

## Usage:

clone this into the directory you want to use for the project, and type

    ./setup.sh

and you're going!

## Config:

You need to set values in config.py:

    API_KEY='...'
    WORKSPACE='...'
    TEAM_NAME'...'

One day there will be magic to list those (other than the API key) for you.

## To Run it:

To run the app with the flask autoreloading magic use

    ./run.py

For production, try:

    ./run.py waitress

## pre-commit hook
There is the [pre-commit script by Sebastian Dahlgren](https://github.com/sebdah/git-pylint-commit-hook) in the .setup/hooks/ folder, which will run pylint on python scripts to check they are valid before you commit them. The setup.sh script will copy this into your .git/hooks by default.

To run a git commit *without* using this, use:

    git commit --no-verify
