import os.path

from setuptools import find_packages, setup


with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

with open('CHANGES.rst', encoding='utf-8') as f:
    history = f.read()

with open(os.path.join('scrapyd_client', 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='scrapyd-client',
    version=version,
    description='A client for Scrapyd',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author='Scrapy developers',
    author_email='info@scrapy.org',
    url='https://github.com/scrapy/scrapyd-client',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    install_requires=[
        'requests',
        'scrapy>=0.17',
        'w3lib',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-console-scripts',
            'pytest-cov',
            'pytest-mock',
        ]
    },
    python_requires='>=3.6',
    license='BSD',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'scrapyd-deploy = scrapyd_client.deploy:main',
            'scrapyd-client = scrapyd_client.cli:main',
        ]
    },
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
