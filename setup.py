
from setuptools import find_packages, setup

requirements = open('requirements.txt').readlines()

config = {
    'description': 'Asynchronous requests using the Scrapy framework',
    'author': 'Josh Levy-Kramer',
    'url': 'https://github.com/joshlk/async_requests',
    'version': '0.1',
    'packages': find_packages(exclude=('tests', 'tests.*')),
    'include_package_data': True,
    'name': 'social_crawler',
    'install_requires': requirements,
}

setup(**config)
