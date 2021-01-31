import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mendec-biojet1",  # Replace with your own username
    version="0.0.1",
    author="biojet1",
    author_email="biojet1@gmail.com",
    description="Message encrytion using RSA algo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biojet1/mendec",
    packages=setuptools.find_packages(),
    install_requires=[
        'ocli @ https://api.github.com/repos/biojet1/ocli/tarball/master',
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
