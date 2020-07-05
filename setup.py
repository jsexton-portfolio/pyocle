import setuptools

import pyocle

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name="pyocle",
    version=pyocle.__version__,
    license='MIT',
    packages=setuptools.find_packages(exclude=('tests',)),
    author="Justin Sexton",
    author_email="justinsexton.dev@gmail.com",
    description="Common library used alongside jsexton-portfolio chalice applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsexton-portfolio/pyocle.git",
    python_requires='>=3',
    keywords=[
        'library',
        'chalice'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
