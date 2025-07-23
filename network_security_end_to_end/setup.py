"""
The setup script for the network_security_end_to_end package.

This file is used to install the package using the following command:

    pip install -e .

This will install the package and its dependencies from the current directory.

The setup.py file is an essential file for Python packages, as it defines the metadata and dependencies required to install the package. 
It is a configuration file that contains information about the package, such as its name, version, author, description, and dependencies.
"""

from setuptools import find_packages, setup
from typing import List

def get_requirements() -> List[str]:
    requirement_list = []
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                requirement = line.strip()
                # ignore empty lines and -e .
                if requirement and requirement != "-e .":
                    requirement_list.append(requirement)

    except FileNotFoundError:
        return []
    
    return requirement_list


setup(
    name="network_security_end_to_end",
    version="0.0.1",
    author="Mushfiqur Rahman",
    author_email="",
    description="A package for network security end to end",    
    packages=find_packages(),
    install_requires=get_requirements()
)