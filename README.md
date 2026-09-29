# Translate Link

This tool generates links to translate a single message into a certain language on TranslateWiki.net.
It’s more convenient this way than having to hand-edit a Special:Translate URL, discover the right message group, etc.

For more information,
please see the tool’s [on-wiki documentation page](https://meta.wikimedia.org/wiki/User:Lucas_Werkmeister/Translate_Link).

## Toolforge setup

On Wikimedia Toolforge, this tool runs under the `translate-link` tool name,
using the [Toolforge Components Service](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Deploy_your_tool) to coordinate
building a container with the [Toolforge Build Service](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Build_Service)
and then deploying that for the webservice and background runner.
The components configuration is in the `toolforge.yaml` file.

To start a new deployment,
run the following command on Toolforge after becoming the tool account:

```sh
toolforge components deployment create
```

This should automatically kick off an image build and restart the webservice at the end.

### Details and troubleshooting

To inspect the overall deployment status, run:

```sh
toolforge components deployment show
```

To debug the image build step, it may be useful to trigger an image build explicitly –
you can add `--ref=foobar` to build from the `foobar` branch instead of the `main` branch:

```sh
toolforge build start https://gitlab.wikimedia.org/toolforge-repos/translate-link
```

The web frontent is a Flask WSGI app using gunicorn,
and runs as the `translate-link` job,
which you may inspect with commands like these:

```sh
toolforge jobs show translate-link
toolforge jobs logs translate-link
kubectl get deployment translate-link
kubectl exec -it deployment/translate-link -- bash
```

### Configuration

The tool reads configuration from both the `config.yaml` file (if it exists)
and from any environment variables starting with `TOOL_*`.
The config file is more convenient for local development;
the environment variables are used on Toolforge:
list them with `toolforge envvars list`.

For the available configuration variables, see the `config.yaml.example` file.

### Update

To update the tool, build a new version of the image as described above,
then restart the webservice:

```sh
toolforge build start --use-latest-versions https://gitlab.wikimedia.org/toolforge-repos/translate-link
webservice restart
```

## Local development setup

You can also run the tool locally, which is much more convenient for development
(for example, Flask will automatically reload the application any time you save a file).

```
git clone https://gitlab.wikimedia.org/toolforge-repos/translate-link.git
cd tool-translate-link
pip3 install -r requirements.txt -r dev-requirements.txt
FLASK_APP=app.py FLASK_ENV=development flask run
```

If you want, you can do this inside some virtualenv too.

## Contributing

To send a patch, you can submit a
[pull request on GitHub](https://github.com/lucaswerkmeister/tool-translate-link) or a
[merge request on GitLab](https://gitlab.wikimedia.org/toolforge-repos/translate-link).
(E-mail / patch-based workflows are also acceptable.)

## License

The code in this repository is released under the AGPL v3, as provided in the `LICENSE` file.
