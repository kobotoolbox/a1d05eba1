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
    entry_points={
        'console_scripts': [
            'a1d05eba1=a1d05eba1.scripts.entry:main'
        ]
    },
    install_requires=[
        'oyaml==0.9',
        'jsonschema==4.4.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

# pytest --cov=a1d05eba1 tests/ --cov-report=html
