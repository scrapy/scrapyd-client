History
-------

2.0.2 (2025-03-08)
~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- ``scrapyd_client.ScrapyClient`` uses the target's URL instead of the target's name when constructing URLs. (Regression in "``scrapyd-client`` raises an error if no Scrapy project is found, like ``scrapyd-deploy``, instead of assuming a target at ``http://localhost:6800``")

2.0.1 (2025-02-12)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- ``scrapyd_client.ScrapyClient.status``

2.0.0 (2024-10-11)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add ``scrapyd-client targets`` subcommand.
- ``scrapyd-client`` can be called as ``python -m scrapyd_client``.
- Add support for Python 3.12.

Changed
^^^^^^^

Changes to commands:

- **BREAKING CHANGE:** ``scrapyd-client`` subcommands accept the ``--target`` (``-t``) option, not the ``scrapyd-client`` command. The target is the name of a target in the ``scrapy.cfg`` file, like ``scrapyd-deploy``, instead of a URL.
- **BREAKING CHANGE:** ``scrapyd-client`` raises an error if no Scrapy project is found, like ``scrapyd-deploy``, instead of assuming a target at ``http://localhost:6800``.
- The ``scrapyd-client schedule`` subcommand accepts multiple ``--arg setting=...`` arguments. (@mxdev88)
- The ``scrapyd_client.ScrapyClient.schedule`` methods accept ``args`` as a list, instead of as a dict.
- The ``scrapyd-deploy --debug`` option prints the subprocess' standard output and standard error, instead of writing to ``stdout`` and ``stderr`` files.

Changes to modules:

- **BREAKING CHANGE:** Move exceptions from ``scrapyd_client.utils`` to ``scrapyd_client.exceptions``.
- **BREAKING CHANGE:** Move ``DEFAULT_TARGET_URL`` and ``HEADERS`` from ``scrapyd_client.utils`` to ``scrapyd_client.pyclient``.
- **BREAKING CHANGE:** Merge ``scrapyd_client.commands`` and ``scrapyd_client.cli`` into ``scrapyd_client.__main__``.

Fixed
^^^^^

- Run ``clean`` separately from building the egg. (Setuptools caches the Python packages from before ``clean`` runs.)
- Add ``pip`` requirement for ``uberegg``.

Removed
^^^^^^^

- **BREAKING CHANGE:** Remove the ``scrapyd-client --username`` (``-u``) and ``--password`` (``-p``) options, in favor of using the ``scrapy.cfg`` file.
- **BREAKING CHANGE:** Remove the ``scrapyd-deploy --list-targets`` (``-l``) option, in favor of ``scrapyd-client targets``.
- **BREAKING CHANGE:** Remove the ``scrapyd-deploy --list-projects`` (``-L``) option, in favor of ``scrapyd-client projects``.
- **BREAKING CHANGE:** Remove the ``get_request`` and ``post_request`` functions from ``scrapyd_client.utils``.
- **BREAKING CHANGE:** Remove the ``scrapyd_client.lib`` module, in favor of ``scrapyd_client.ScrapydClient``.
- Remove ``urllib3`` and ``w3lib`` requirements.
- Drop support for Python 3.7, 3.8.

1.2.3 (2023-01-30)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add ``scrapyd-client --username`` and ``--password`` options. (@mxdev88)
- Add ``ScrapydClient``, a Python client to interact with Scrapyd. (@mxdev88)
- Expand environment variables in the ``scrapy.cfg`` file. (@mxdev88)
- Add support for Python 3.10, 3.11. (@Laerte)

1.2.2 (2022-05-03)
~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- Fix ``FileNotFoundError`` when using ``scrapyd-deploy --deploy-all-targets``.

1.2.1 (2022-05-02)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add ``scrapyd-deploy --include-dependencies`` option to install project dependencies from a ``requirements.txt`` file. (@mxdev88)

Changed
^^^^^^^

Fixed
^^^^^

- Remove temporary directories created by ``scrapyd-deploy --deploy-all-targets``.
- Address ``w3lib`` deprecation warning, by adding ``urllib3`` requirement.
- Address Python deprecation warnings.

1.2.0 (2021-10-01)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add support for Scrapy 2.5.
- Add support for Python 3.7, 3.8, 3.9, PyPy3.7.

Removed
^^^^^^^

- Remove ``scrapyd_client.utils.get_config``, which was a compatibility wrapper for Python 2.7.
- Drop support for Python 2.7, 3.4, 3.5.

1.2.0a1 (2017-08-24)
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add ``scrapyd-client`` console script with ``deploy``, ``projects``, ``spiders`` and ``schedule`` subcommands.
- Install ``scrapyd-deploy`` as a console script.

1.1.0 (2017-02-10)
~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add ``scrapyd-deploy --deploy-all-targets`` (``-a``) option to deploy to all targets.
- Add support for Python 3.

Fixed
^^^^^

- Fix returncode on egg deploy error.

Removed
^^^^^^^

- Drop support for Python 2.6.

1.0.1 (2015-04-09)
~~~~~~~~~~~~~~~~~~

Initial release.
