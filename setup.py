from setuptools import setup, find_packages

setup(
    name="croc",
    version="0.1.0",
    description="X?ChaCha{8,12,20} crypto cores.",
    author="vikrrrr",
    author_email="vikr@protonmail.com",
    license="MIT",
    install_requires=["nmigen>=0.2", "pytest>=6.0.0"],
    packages=find_packages(),
)
