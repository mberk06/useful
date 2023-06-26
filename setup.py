from setuptools import setup, find_packages

setup(
    name="useful",
    version="0.1.0",
    url="https://github.com/mberk06/useful",
    author="Michael Berk",
    author_email="michaelberk99@gmail.com",
    description="Code I use a lot.",
    packages=find_packages(),
    install_requires=["requests", "tenacity", "pydantic"],
)
