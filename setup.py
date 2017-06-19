from os.path import join, dirname

with open(join(dirname(__file__), 'scrapyd_client/VERSION')) as f:
    version = f.read().strip()

setup_args = {
    'name': 'scrapyd-client',
    'version': version,
    'url': 'https://github.com/scrapy/scrapyd-client',
    'description': 'A client for scrapyd',
    'long_description': open('README.rst').read(),
    'author': 'Scrapy developers',
    'maintainer': 'Scrapy developers',
    'maintainer_email': 'info@scrapy.org',
    'license': 'BSD',
    'packages': ['scrapyd_client'],
    'entry_points': {
        'console_scripts': ['scrapyd-deploy = scrapyd_client.deploy:main',
                            'scrapyd-client = scrapyd_client.cli:main']
    },
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Topic :: Internet :: WWW/HTTP',
    ],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    setup_args['install_requires'] = ['requests', 'Scrapy>=0.17', 'six']

setup(**setup_args)
