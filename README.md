# python-500px-sitebuilder

A Python script that generates a gallery/thumbnail page from your 500px.com account.

It's based on the ```500px/python-500px``` project, extends a bit the base library and adds a site generator. All
modifications compared to the original library are located in the ```sitebuilder``` directory,
everything else is untouched. All code is located in the
file ```sitebuilder/sitebuilder.py``` file, which also contains the extended API interface class ```FiveHundredPXAPIEx```.

## Installation and Usage

1) Clone this repo into your github account.
2) Get your API key at [https://500px.com/settings/applications]
3) Modify ```prefix.html``` and ```suffix.html``` to build your personal layout.
4) Modify ```sitebuilder.py```: Configuration (4 constants at the top, out_photo_description(), etc.). No magic, just have a look.
5) Run the script, potentially using a cron job on your web server

The script creates a ```out``` directory at the place specified in ```_BASEDIR``` Everything will be there.

## Requires
  * simplejson (from original project)

## License

HAVEFUN 1.0

MIT (as the original project)
