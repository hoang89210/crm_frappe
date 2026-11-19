from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in pushesale/__init__.py
from pushesale import __version__ as version

setup(
	name="pushesale",
	version=version,
	description="Frappe app replacing basic Pushsale (CRM Lead + Chatwoot + SIM calls)",
	author="Dev",
	author_email="dev@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
