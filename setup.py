import os

from setuptools import find_packages, setup

setup(
    name="pwned-passwords-django",
    zip_safe=False,  # eggs are the devil.
    version="1.6.1",
    description="A Pwned Passwords implementation for Django sites.",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    author="James Bennett",
    author_email="james@b-list.org",
    url="https://github.com/ubernostrum/pwned-passwords-django/",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=["Django>=3.2", "requests"],
)
