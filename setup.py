import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="a1d05eba1-dorey",
    version="0.1",
    author="Alex Dorey",
    author_email="alex.dorey@kobotoolbox.org",
    description="A package to migrate XLSForm content to match a schema",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dorey/a1d05eba1",
    packages=setuptools.find_packages(),
    package_data={'': [
        'yml/*.yml',
        'yml/*/*.yml',
        'yml/*/*/*.yml',
    ]},
    install_requires=[
        'pytest==5.4.3',
        'frozendict==1.2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

# pytest --cov=a1d05eba1 tests/ --cov-report=html
