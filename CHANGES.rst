History
-------

Unreleased
~~~~~~~~~~

- ``scrapyd-deploy``: ``--list-projects`` (``-L``) now uses the ``TARGET`` positional argument instead of accepting a ``TARGET`` option.
- Address deprecation warnings.
- Add dependency on ``urllib3``.


1.2.0 (2021-10-01)
~~~~~~~~~~~~~~~~~~

- Add support for Scrapy 2.5.
- Add support for Python 3.7, 3.8, 3.9, PyPy3.7.
- Drop support for Python 2.7, 3.4, 3.5.
- Remove ``scrapyd_client.utils.get_config``, which was a compatibility wrapper for Python 2.7.


1.2.0a1 (2017-08-24)
~~~~~~~~~~~~~~~~~~~~

- Install ``scrapyd-deploy`` as a console script.
- New ``scrapyd-client`` CLI with ``deploy``, ``projects``, ``spiders``,
  and ``schedule`` subcommands.


1.1.0 (2017-02-10)
~~~~~~~~~~~~~~~~~~

- New ``-a`` option to deploy to all targets.
- Fix returncode on egg deploy error.
- Add Python 3 support.
- Drop Python 2.6 support.


1.0.1 (2015-04-09)
~~~~~~~~~~~~~~~~~~

Initial release.
