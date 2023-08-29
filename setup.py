from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in german_accounting/__init__.py
from german_accounting import __version__ as version

setup(
	name="german_accounting",
	version=version,
	description="ERPNext Enhancement for IMAT",
	author="phamos.eu",
	author_email="furqan.asghar@phamos.eu",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
