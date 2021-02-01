import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mendec",
    version="0.0.1",
    author="biojet1",
    author_email="biojet1@gmail.com",
    description="Message encrytion using RSA algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biojet1/mendec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
