==============
Scrapyd-client
==============

.. image:: https://secure.travis-ci.org/scrapy/scrapyd-client.png?branch=master
   :target: http://travis-ci.org/scrapy/scrapyd-client

Scrapyd-client is a client for Scrapyd_. It provides the general ``scrapyd-client`` and the
``scrapyd-deploy`` utility which allows you to deploy your project to a Scrapyd server.

.. _Scrapyd: https://scrapyd.readthedocs.io


scrapyd-client
--------------

For a reference on each subcommand invoke ``scrapyd-client <subcommand> --help``.

Where filtering with wildcards is possible, it is facilitated with fnmatch_.
The ``--project`` option can be omitted if one is found in a ``scrapy.cfg``.

.. _fnmatch: https://docs.python.org/library/fnmatch.html

deploy
~~~~~~

At the moment this is a wrapper around `scrapyd-deploy`_. Note that the command line options
of this one are likely to change.

projects
~~~~~~~~

Lists all projects of a Scrapyd instance::

   # lists all projects on the default target
   scrapyd-client projects
   # lists all projects from a custom URL
   scrapyd-client -t http://scrapyd.example.net projects

schedule
~~~~~~~~

Schedules one or more spiders to be executed::

   # schedules any spider
   scrapyd-client schedule
   # schedules all spiders from the 'knowledge' project
   scrapyd-client schedule -p knowledge \*
   # schedules any spider from any project whose name ends with '_daily'
   scrapyd-client schedule -p \* *_daily

spiders
~~~~~~~

Lists spiders of one or more projects::

   # lists all spiders
   scrapyd-client spiders
   # lists all spiders from the 'knowledge' project
   scrapyd-client spiders -p knowledge


scrapyd-deploy
--------------

How It Works
~~~~~~~~~~~~

Deploying your project to a Scrapyd server typically involves two steps:

1. Eggifying_ your project. You'll need to install setuptools_ for this. See `Egg Caveats`_ below.
2. Uploading the egg to the Scrapyd server through the `addversion.json`_ endpoint.

The ``scrapyd-deploy`` tool automates the process of building the egg and pushing it to the target
Scrapyd server.

.. _addversion.json:  https://scrapyd.readthedocs.org/en/latest/api.html#addversion-json
.. _Eggifying: http://peak.telecommunity.com/DevCenter/PythonEggs
.. _setuptools: https://pypi.python.org/pypi/setuptools

Deploying a Project
~~~~~~~~~~~~~~~~~~~

First ``cd`` into your project's root, you can then deploy your project with the following::

    scrapyd-deploy <target> -p <project>

This will eggify your project and upload it to the target. If you have a ``setup.py`` file in your
project, it will be used, otherwise one will be created automatically.

If successful you should see a JSON response similar to the following::

    Deploying myproject-1287453519 to http://localhost:6800/addversion.json
    Server response (200):
    {"status": "ok", "spiders": ["spider1", "spider2"]}

To save yourself from having to specify the target and project, you can set the defaults in the
``scrapy.cfg`` file::

    [deploy]
    url = http://scrapyd.example.com/api/scrapyd
    username = scrapy
    password = secret
    project = yourproject


You can now deploy your project with just the following::

    scrapyd-deploy

If you have more than one target to deploy, you can deploy your project in all targets with one
command::

      scrapyd-deploy -a -p <project>

Versioning
~~~~~~~~~~

By default, ``scrapyd-deploy`` uses the current timestamp for generating the project version, as
shown above. However, you can pass a custom version using ``--version``::

    scrapyd-deploy <target> -p <project> --version <version>

Or for all targets::

    scrapyd-deploy -a -p <project> --version <version>

The version must be comparable with LooseVersion_. Scrapyd will use the greatest version unless
specified.

If you use Mercurial or Git, you can use ``HG`` or ``GIT`` respectively as the argument supplied to
``--version`` to use the current revision as the version. You can save yourself having to specify
the version parameter by adding it to your target's entry in ``scrapy.cfg``::

    [deploy:target]
    ...
    version = HG

.. _LooseVersion: http://epydoc.sourceforge.net/stdlib/distutils.version.LooseVersion-class.html

Local Settings
~~~~~~~~~~~~~~

You may want to keep certain settings local and not have them deployed to Scrapyd. To accomplish
this you can create a ``local_settings.py`` file at the root of your project, where your
``scrapy.cfg`` file resides, and add the following to your project's settings::

    try:
        from local_settings import *
    except ImportError:
        pass

``scrapyd-deploy`` doesn't deploy anything outside of the project module, so the
``local_settings.py`` file won't be deployed.

Egg Caveats
~~~~~~~~~~~

Some things to keep in mind when building eggs for your Scrapy project:

* Make sure no local development settings are included in the egg when you build it. The
  ``find_packages`` function may be picking up your custom settings. In most cases you want to
  upload the egg with the default project settings.
* You should avoid using ``__file__`` in your project code as it doesn't play well with eggs.
  Consider using `pkgutil.get_data`_ instead.
* Be careful when writing to disk in your project, as Scrapyd will most likely be running under a
  different user which may not have write access to certain directories. If you can, avoid writing
  to disk and always use tempfile_ for temporary files.

.. _pkgutil.get_data: http://docs.python.org/library/pkgutil.html#pkgutil.get_data
.. _tempfile: http://docs.python.org/library/tempfile.html


Global settings
---------------

Targets
~~~~~~~

You can define Scrapyd targets in your project's ``scrapy.cfg`` file. Example::

    [deploy:example]
    url = http://scrapyd.example.com/api/scrapyd
    username = scrapy
    password = secret

While your target needs to be defined with its URL in ``scrapy.cfg``,
you can use netrc_ for username and password, like so::

    machine scrapyd.example.com
        username scrapy
        password secret

If you want to list all available targets, you can use the ``-l`` option::

    scrapyd-deploy -l

To list projects available on a specific target, use the ``-L`` option::

    scrapyd-deploy -L example

.. _netrc: https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html
