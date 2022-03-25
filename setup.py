from setuptools import setup, find_packages

setup(
    name="croc",
    version="0.2.0",
    description="X?ChaCha{8,12,20} crypto cores.",
    author="vikrrrr",
    author_email="vikr@protonmail.com",
    license="GPL-3.0-or-later",
    install_requires=["amaranth>=0.3"],
    packages=find_packages(),
)
