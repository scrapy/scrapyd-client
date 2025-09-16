# Scrapyd Client

[![PyPI Version](https://img.shields.io/pypi/v/scrapyd-client.svg)](https://pypi.org/project/scrapyd-client/)
[![Build Status](https://github.com/scrapy/scrapyd-client/workflows/Tests/badge.svg)](https://github.com/scrapy/scrapyd-client/actions)
[![Coverage Status](https://codecov.io/gh/scrapy/scrapyd-client/branch/master/graph/badge.svg)](https://codecov.io/gh/scrapy/scrapyd-client)
[![Python Version](https://img.shields.io/pypi/pyversions/scrapyd-client.svg)](https://pypi.org/project/scrapyd-client/)
[![License](https://img.shields.io/pypi/l/scrapyd-client.svg)](https://github.com/scrapy/scrapyd-client/blob/master/LICENSE)

A feature-rich client for [Scrapyd](https://scrapyd.readthedocs.io) with enhanced CLI tools and Python API for managing Scrapy projects on remote servers.

## ✨ Features

### 🛠️ Command Line Tools
- **`scrapyd-deploy`** - Deploy Scrapy projects to Scrapyd servers with rich output formatting
- **`scrapyd-client`** - Comprehensive CLI for managing deployed projects

### 🐍 Python API
- **`ScrapydClient`** - Full-featured Python client with security enhancements and connection pooling

### 🎨 Enhanced User Experience
- **Rich formatting** - Beautiful, colored CLI output with clear error messages
- **Security features** - SSL/TLS support, authentication, and connection validation
- **Configuration flexibility** - Environment variable expansion and multiple deployment targets

## 🚀 Quick Start

### Installation

```bash
pip install scrapyd-client
```

### Basic Usage

```bash
# Deploy a project
scrapyd-deploy production -p myproject

# List projects on a server
scrapyd-client projects

# Schedule a spider
scrapyd-client schedule -p myproject myspider

# List all spiders
scrapyd-client spiders
```

## 📖 Documentation

### scrapyd-deploy

Deploy your Scrapy projects to Scrapyd servers with ease.

#### Basic Deployment

1. Navigate to your project directory (containing `scrapy.cfg`)
2. Deploy your project:

```bash
scrapyd-deploy <target> -p <project>
```

**Example:**
```bash
scrapyd-deploy production -p ecommerce-scraper
```

#### 🎯 Advanced Features

**Custom Versioning:**
```bash
# Use timestamp (default)
scrapyd-deploy production -p myproject

# Use custom version
scrapyd-deploy production -p myproject --version 2.1.0

# Use Git revision
scrapyd-deploy production -p myproject --version GIT

# Use Mercurial revision
scrapyd-deploy production -p myproject --version HG
```

**Include Dependencies:**
```bash
# Deploy with requirements.txt dependencies
scrapyd-deploy --include-dependencies
```

**Build Only (No Deploy):**
```bash
# Build egg without deploying
scrapyd-deploy --build-egg=./dist/myproject.egg
```

**Deploy to All Targets:**
```bash
# Deploy to all configured targets
scrapyd-deploy -a -p myproject
```

#### 📁 Project Structure

Your project should have this structure:
```
myproject/
├── scrapy.cfg          # Scrapy configuration
├── setup.py           # Python package setup (auto-generated if missing)
├── requirements.txt    # Dependencies (optional)
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── spiders/
│   └── ...
```

#### 🔧 Setup.py Configuration

If you have a custom `setup.py`, ensure it includes the entry points:

```python
from setuptools import setup, find_packages

setup(
    name='myproject',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'scrapy': ['settings = myproject.settings']
    },
    # Include data files
    package_data={
        'myproject': ['data/*.json', 'templates/*.html']
    },
    include_package_data=True,
)
```

### scrapyd-client

Comprehensive CLI for managing your deployed Scrapy projects.

#### Available Commands

**`targets`** - List all configured targets:
```bash
scrapyd-client targets
```

**`projects`** - List projects on Scrapyd servers:
```bash
# List all projects on default target
scrapyd-client projects

# List projects on specific target
scrapyd-client -t http://scrapyd.example.com projects
```

**`spiders`** - List available spiders:
```bash
# List all spiders from all projects
scrapyd-client spiders

# List spiders from specific project
scrapyd-client spiders -p myproject
```

**`schedule`** - Schedule spider executions:
```bash
# Schedule all spiders
scrapyd-client schedule

# Schedule specific spider
scrapyd-client schedule -p myproject myspider

# Schedule with custom settings
scrapyd-client schedule -p myproject myspider \
  --arg 'setting=DOWNLOAD_DELAY=2' \
  --arg 'setting=CONCURRENT_REQUESTS=1'

# Schedule all spiders matching pattern
scrapyd-client schedule -p myproject "*_daily"
```

**`deploy`** - Deploy projects (wrapper around scrapyd-deploy):
```bash
scrapyd-client deploy -p myproject
```

### ScrapydClient Python API

Interact with Scrapyd programmatically with enhanced security and features.

#### Basic Usage

```python
from scrapyd_client import ScrapydClient

# Connect to Scrapyd server
client = ScrapydClient('http://localhost:6800')

# List projects
projects = client.projects()
print("Available projects:", projects)

# List spiders for a project
spiders = client.spiders(project='myproject')
print("Available spiders:", spiders)

# Schedule a spider
jobid = client.schedule('myproject', 'myspider', arg1='value1')
print(f"Scheduled job: {jobid}")

# Check job status
jobs = client.jobs(project='myproject')
print("Running jobs:", jobs['running'])
```

#### 🔒 Advanced Security Features

```python
# Secure connection with authentication
client = ScrapydClient(
    url='https://scrapyd.example.com:6801',
    username='admin',
    password='secret',
    verify_ssl=True,
    timeout=30.0
)

# Mutual TLS authentication
client = ScrapydClient(
    url='https://secure-scrapyd.example.com',
    cert_file='/path/to/client.crt',
    key_file='/path/to/client.key',
    ca_bundle='/path/to/ca-bundle.crt'
)

# Health check
health = client.health_check()
print("Server health:", health)

# Context manager for automatic cleanup
with ScrapydClient('http://localhost:6800') as client:
    projects = client.projects()
    # Connection automatically closed
```

#### 🔧 Available Methods

| Method | Description | Example |
|--------|-------------|---------|
| `projects(pattern="*")` | List projects | `client.projects("web_*")` |
| `spiders(project, pattern="*")` | List spiders | `client.spiders("myproject", "*_daily")` |
| `jobs(project=None)` | List jobs | `client.jobs("myproject")` |
| `schedule(project, spider, **args)` | Schedule spider | `client.schedule("proj", "spider", arg1="val")` |
| `cancel(project, jobid)` | Cancel job | `client.cancel("myproject", "abc123")` |
| `health_check()` | Server health | `client.health_check()` |

## ⚙️ Configuration

Configure targets in your `scrapy.cfg` file:

### Single Target

```ini
[deploy]
url = http://scrapyd.example.com:6800
username = admin
password = secret
project = myproject
version = GIT
```

### Multiple Targets

```ini
[deploy:production]
url = https://scrapyd-prod.example.com:6801
username = admin
password = ${SCRAPYD_PROD_PASSWORD}

[deploy:staging]
url = http://scrapyd-staging.example.com:6800
username = dev
password = ${SCRAPYD_STAGING_PASSWORD}

[deploy:local]
url = http://localhost:6800
```

### 🔐 Environment Variables

Keep secrets secure using environment variables:

```ini
[deploy]
url = ${SCRAPYD_URL}
username = ${SCRAPYD_USERNAME}
password = ${SCRAPYD_PASSWORD}
```

Or use the alternative syntax:
```ini
[deploy]
url = $SCRAPYD_URL
username = $SCRAPYD_USERNAME
password = $SCRAPYD_PASSWORD
```

### 🏠 Netrc Support

You can also use `.netrc` for credentials:

```
machine scrapyd.example.com
    login admin
    password secret
```

## 💡 Best Practices

### 🏗️ Project Structure
- Keep a clean `requirements.txt` for dependencies
- Use `.gitignore` to exclude build artifacts
- Separate local and production settings

### 🔧 Development Workflow
```bash
# 1. Test locally
scrapy crawl myspider

# 2. Deploy to staging
scrapyd-deploy staging -p myproject

# 3. Test on staging
scrapyd-client schedule -t staging -p myproject myspider

# 4. Deploy to production
scrapyd-deploy production -p myproject
```

### 📦 Managing Dependencies

Create a `requirements.txt`:
```
scrapy>=2.5.0
requests>=2.25.0
beautifulsoup4>=4.9.0
```

Deploy with dependencies:
```bash
scrapyd-deploy --include-dependencies
```

### 🗂️ Local Settings

Keep development settings separate:

1. Create `local_settings.py`:
```python
# Development-only settings
LOG_LEVEL = 'DEBUG'
ROBOTSTXT_OBEY = False
```

2. Import in your main settings:
```python
# settings.py
try:
    from .local_settings import *
except ImportError:
    pass
```

## 🐛 Troubleshooting

### Common Issues

**❌ Settings file included in egg**
- **Solution**: Use local settings pattern or exclude from `find_packages()`:
```python
packages=find_packages(exclude=["myproject.dev_settings"])
```

**❌ `__file__` doesn't work in Scrapyd**
- **Problem**: `__file__` is not available in eggs
- **Solution**: Use `pkgutil.get_data()`:
```python
import pkgutil
data = pkgutil.get_data("myproject", "data/config.json")
```

**❌ Permission denied when writing files**
- **Problem**: Scrapyd runs under different user
- **Solution**: Use `tempfile` for temporary files:
```python
import tempfile
with tempfile.NamedTemporaryFile() as f:
    # Write temporary data
    pass
```

**❌ Connection refused**
- **Check**: Is Scrapyd server running?
- **Check**: Is the URL and port correct?
- **Check**: Firewall and network connectivity

**❌ SSL certificate errors**
- **For development**: Use `verify_ssl=False` (not recommended for production)
- **For production**: Ensure valid SSL certificates

### 🌐 Proxy Support

Use standard environment variables:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1
```

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/scrapy/scrapyd-client.git
cd scrapyd-client

# Install in development mode
pip install -e .[test]

# Run tests
pytest

# Run linting
ruff check
ruff format
```

## 📄 License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Scrapyd](https://scrapyd.readthedocs.io) - The Scrapy daemon this client connects to
- [Scrapy](https://scrapy.org) - The web scraping framework
- [Scrapyd-web](https://github.com/my8100/scrapyd-web) - Web UI for Scrapyd management

## 📚 Resources

- [Documentation](https://scrapyd-client.readthedocs.io) (coming soon)
- [Scrapy Configuration](https://docs.scrapy.org/en/latest/topics/settings.html#how-to-access-settings)
- [Scrapyd API Reference](https://scrapyd.readthedocs.io/en/stable/api.html)

---

Made with ❤️ by the [Scrapy](https://scrapy.org) community