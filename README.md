## Asana view.

Simple display of asana tasks for team screens.  Simple Python-based web server, which then can be displayed
on any browser.  We run the server and client on a single raspberry pi computer with a big plasma screen attached.

Written for internal use at [OMNIvision](http://omnivision.om.org), MIT Licence.

## Usage:

Either download or git clone this repository to wherever you want.  In a terminal go
to that directory, and type:

    ./setup.sh

This will download all the dependencies, and set it all up (hopefully).

## Requirements:

You will need Python 2.7+, and gcc / a C compiler (to compile the gevent stuff).
You won't actually have to compile anything yourself, the `setup.sh` script will do that.

## Config:

You need to set your API_KEY in config.py:

    API_KEY='...'

You can get your API_KEY from asana.  In your 'Account Settings' / 'APPs' (click your name in the bottom of the left sidebar).

Asana-view will then use your 'default' workspace tasks when you run it.
To choose a different workspace, set `WORKSPACE="..."` in your config.py.
When you run asana-view without a configured workspace, it will tell you
what the options are.

By default, Asana-view will cache all requests from asana for about a minute and a half, so that you don't max out your asana requests.  If you want to disable the caching (not recommended), then in your config.py:

    USECACHE=False

## To Run it:

To run the app:

    ./run.py

and then point a web browser at `http://localhost:5000/`.
