==============
Scrapyd-client
==============

|PyPI Version| |Build Status| |Coverage Status| |Python Version|

Scrapyd-client is a client for Scrapyd_. It provides:

Command line tools:

-  ``scrapyd-deploy``, to deploy your project to a Scrapyd server
-  ``scrapyd-client``, to interact with your project once deployed

Python client:

-  ``ScrapydClient``, to interact with Scrapyd within your python code

It is configured using the `Scrapy configuration file`_.

.. _Scrapyd: https://scrapyd.readthedocs.io
.. |PyPI Version| image:: https://img.shields.io/pypi/v/scrapyd-client.svg
   :target: https://pypi.org/project/scrapyd-client/
.. |Build Status| image:: https://github.com/scrapy/scrapyd-client/workflows/Tests/badge.svg
.. |Coverage Status| image:: https://codecov.io/gh/scrapy/scrapyd-client/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/scrapy/scrapyd-client
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/scrapyd-client.svg
   :target: https://pypi.org/project/scrapyd-client/


scrapyd-deploy
--------------

Deploying your project to a Scrapyd server involves:

#. `Eggifying <https://setuptools.pypa.io/en/latest/deprecated/python_eggs.html>`__ your project.
#. Uploading the egg to the Scrapyd server through the `addversion.json <https://scrapyd.readthedocs.org/en/latest/api.html#addversion-json>`__ webservice.

The ``scrapyd-deploy`` tool automates the process of building the egg and pushing it to the target Scrapyd server.

Deploying a project
~~~~~~~~~~~~~~~~~~~

#. Change (``cd``) to the root of your project (the directory containing the ``scrapy.cfg`` file)
#. Eggify your project and upload it to the target:

   .. code-block:: shell

      scrapyd-deploy <target> -p <project>

If you don't have a ``setup.py`` file in the root of your project, one will be created. If you have one, it must set the ``entry_points`` keyword argument in the ``setup()`` function call, for example:

   .. code-block:: python

      setup(
          name         = 'project',
          version      = '1.0',
          packages     = find_packages(),
          entry_points = {'scrapy': ['settings = projectname.settings']},
      )

If the command is successful, you should see a JSON response, like:

.. code-block:: none

   Deploying myproject-1287453519 to http://localhost:6800/addversion.json
   Server response (200):
   {"status": "ok", "spiders": ["spider1", "spider2"]}

To save yourself from having to specify the target and project, you can configure your defaults in the `Scrapy configuration file`_.

Versioning
~~~~~~~~~~

By default, ``scrapyd-deploy`` uses the current timestamp for generating the project version. You can pass a custom version using ``--version``:

.. code-block:: shell

   scrapyd-deploy <target> -p <project> --version <version>

See `Scrapyd's documentation <https://scrapyd.readthedocs.io/en/latest/overview.html>`__ on how it determines the latest version.

If you use Mercurial or Git, you can use ``HG`` or ``GIT`` respectively as the argument supplied to
``--version`` to use the current revision as the version. You can save yourself having to specify
the version parameter by adding it to your target's entry in ``scrapy.cfg``:

.. code-block:: ini

   [deploy]
   ...
   version = HG

Note: The ``version`` keyword argument in the ``setup()`` function call in the ``setup.py`` file has no meaning to Scrapyd.

Include dependencies
~~~~~~~~~~~~~~~~~~~~

#. Create a `requirements.txt <https://pip.pypa.io/en/latest/reference/requirements-file-format/>`__ file at the root of your project, alongside the ``scrapy.cfg`` file
#. Use the ``--include-dependencies`` option when building or deploying your project:

   .. code-block:: bash

      scrapyd-deploy --include-dependencies

Alternatively, you can install the dependencies directly on the Scrapyd server.

Include data files
~~~~~~~~~~~~~~~~~~

#. Create a ``setup.py`` file at the root of your project, alongside the ``scrapy.cfg`` file, if you don't have one:

   .. code-block:: shell

      scrapyd-deploy --build-egg=/dev/null

#. Set the ``package_data`` and ``include_package_data` keyword arguments in the ``setup()`` function call in the ``setup.py`` file. For example:

   .. code-block:: python

      from setuptools import setup, find_packages

      setup(
          name         = 'project',
          version      = '1.0',
          packages     = find_packages(),
          entry_points = {'scrapy': ['settings = projectname.settings']},
          package_data = {'projectname': ['path/to/*.json']},
          include_package_data = True,
      )

Local settings
~~~~~~~~~~~~~~

You may want to keep certain settings local and not have them deployed to Scrapyd.

#. Create a ``local_settings.py`` file at the root of your project, alongside the ``scrapy.cfg`` file
#. Add the following to your project's settings file:

   .. code-block:: python

      try:
          from local_settings import *
      except ImportError:
          pass

``scrapyd-deploy`` doesn't deploy anything outside of the project module, so the ``local_settings.py`` file won't be deployed.

Troubleshooting
~~~~~~~~~~~~~~~

-  Problem: A settings file for local development is being included in the egg.

   Solution: See `Local settings`_. Or, exclude the module from the egg. If using scrapyd-client's default ``setup.py`` file, change the ``find_package()`` call:

   .. code-block:: python

      setup(
          name         = 'project',
          version      = '1.0',
          packages     = find_packages(),
          entry_points = {'scrapy': ['settings = projectname.settings']},
      )

   to:

   .. code-block:: python

      setup(
          name         = 'project',
          version      = '1.0',
          packages     = find_packages(exclude=["myproject.devsettings"]),
          entry_points = {'scrapy': ['settings = projectname.settings']},
      )

-  Problem: Code using ``__file__`` breaks when run in Scrapyd.

   Solution: Use `pkgutil.get_data <https://docs.python.org/library/pkgutil.html#pkgutil.get_data>`__ instead. For example, change:

   .. code-block:: python

      path = os.path.dirname(os.path.realpath(__file__))  # BAD
      open(os.path.join(path, "tools", "json", "test.json"), "rb").read()

   to:

   .. code-block:: python

      import pkgutil
      pkgutil.get_data("projectname", "tools/json/test.json")

-  Be careful when writing to disk in your project, as Scrapyd will most likely be running under a
   different user which may not have write access to certain directories. If you can, avoid writing
   to disk and always use `tempfile <https://docs.python.org/library/tempfile.html>`__ for temporary files.

-  If you use a proxy, use the ``HTTP_PROXY``, ``HTTPS_PROXY``, ``NO_PROXY`` and/or ``ALL_PROXY`` environment variables,
   as documented by the `requests <https://docs.python-requests.org/en/latest/user/advanced/#proxies>`__ package.

scrapyd-client
--------------

For a reference on each subcommand invoke ``scrapyd-client <subcommand> --help``.

Where filtering with wildcards is possible, it is facilitated with `fnmatch <https://docs.python.org/library/fnmatch.html>`__.
The ``--project`` option can be omitted if one is found in a ``scrapy.cfg``.

deploy
~~~~~~

This is a wrapper around `scrapyd-deploy`_.

targets
~~~~~~~

Lists all targets:

   scrapyd-client targets

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
   scrapyd-client schedule -p \* \*_daily
   # schedules spider1 in project1 specifying settings
   scrapyd-client schedule -p project1 spider1 --arg 'setting=DOWNLOADER_MIDDLEWARES={"my.middleware.MyDownloader": 610}'

spiders
~~~~~~~

Lists spiders of one or more projects::

   # lists all spiders
   scrapyd-client spiders
   # lists all spiders from the 'knowledge' project
   scrapyd-client spiders -p knowledge

ScrapydClient
-------------

Interact with Scrapyd within your python code.

.. code-block:: python

   from scrapyd_client import ScrapydClient
   client = ScrapydClient()

   for project in client.projects():
      print(client.jobs(project=project))


Scrapy configuration file
-------------------------

Targets
~~~~~~~

You can define a Scrapyd target in your project's ``scrapy.cfg`` file. Example:

.. code-block:: ini

   [deploy]
   url = http://scrapyd.example.com/api/scrapyd
   username = scrapy
   password = secret
   project = projectname

You can now deploy your project without the ``<target>`` argument or ``-p <project>`` option::

   scrapyd-deploy

If you have multiple targets, add the target name in the section name. Example:

.. code-block:: ini

   [deploy:targetname]
   url = http://scrapyd.example.com/api/scrapyd

   [deploy:another]
   url = http://other.example.com/api/scrapyd

If you are working with CD frameworks, you do not need to commit your secrets to your repository. You can use environment variable expansion like so:

.. code-block:: ini

   [deploy]
   url = $SCRAPYD_URL
   username = $SCRAPYD_USERNAME
   password = $SCRAPYD_PASSWORD

or using this syntax:

.. code-block:: ini

   [deploy]
   url = ${SCRAPYD_URL}
   username = ${SCRAPYD_USERNAME}
   password = ${SCRAPYD_PASSWORD}

To deploy to one target, run::

   scrapyd-deploy targetname -p <project>

To deploy to all targets, use the ``-a`` option::

   scrapyd-deploy -a -p <project>

While your target needs to be defined with its URL in ``scrapy.cfg``,
you can use `netrc <https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html>`__ for username and password, like so::

   machine scrapyd.example.com
       login scrapy
       password secret
