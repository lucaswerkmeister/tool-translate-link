# Translate Link

This tool generates links to translate a single message into a certain language on TranslateWiki.net.
It’s more convenient this way than having to hand-edit a Special:Translate URL, discover the right message group, etc.

For more information,
please see the tool’s [on-wiki documentation page](https://meta.wikimedia.org/wiki/User:Lucas_Werkmeister/Translate_Link).

## Toolforge setup

On Wikimedia Toolforge, this tool runs under the `translate-link` tool name.
Source code resides in `~/www/python/src/`,
a virtual environment is set up in `~/www/python/venv/`,
logs end up in `~/uwsgi.log`.

If the web service is not running for some reason, run the following command:
```
webservice start
```
If it’s acting up, try the same command with `restart` instead of `start`.
Both should pull their config from the `service.template` file,
which is symlinked from the source code directory into the tool home directory.

To update the service, run the following commands after becoming the tool account:
```
webservice shell
source ~/www/python/venv/bin/activate
cd ~/www/python/src
git fetch
git diff @ @{u} # inspect changes
git merge --ff-only @{u}
pip3 install -r requirements.txt
webservice restart
```

## Local development setup

You can also run the tool locally, which is much more convenient for development
(for example, Flask will automatically reload the application any time you save a file).

```
git clone https://phabricator.wikimedia.org/source/tool-translate-link.git
cd tool-translate-link
pip3 install -r requirements.txt
FLASK_APP=app.py FLASK_ENV=development flask run
```

If you want, you can do this inside some virtualenv too.

## Contributing

To send a patch, you can use any of the following methods:

* [Submit a pull request on GitHub.](https://github.com/lucaswerkmeister/tool-translate-link)
* Use `git send-email`.
  (Send the patch(es) to the email address from the Git commit history.)
* Upload the changes to a repository of your own and use `git request-pull` (same email address).
* Upload a diff on [GitHub Gist](https://gist.github.com/)
  and send the link to the tool’s maintainer(s) via email, Twitter, on-wiki message, or whatever.
* [Create a Diff on Phabricator.](https://phabricator.wikimedia.org/differential/diff/create/)
  Make sure to add @LucasWerkmeister as subscriber.

They’re listed in the maintainer(s)’ order of preference, from most to least preferred,
but feel free to use any of these methods as it best suits you.

## License

The code in this repository is released under the AGPL v3, as provided in the `LICENSE` file.
