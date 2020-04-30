import os

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_version():
    filename = os.path.join(os.path.dirname(__file__), "kultur", "__init__.py")
    with open(filename, mode="r", encoding="utf-8") as fin:
        for line in fin:
            if line and line.strip() and line.startswith("__version__"):
                return line.split("=")[1].strip().strip("'")

    return "0.0.0.0"


setup(
    name="kultur",
    version=read_version(),
    url="https://github.com/niekstortenbeker/kultur",
    license="MIT",
    author="Niek Stortenbeker",
    author_email="niek@kulturbremen.de",
    description="Collect programs from a selection of theaters in Bremen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=find_packages(exclude=("tests",)),
    packages=find_packages(),  # for "kultur -f" I need tests also
    include_package_data=True,
    install_requires=[
        "emoji",
        "requests",
        "arrow",
        "beautifulsoup4",
        "click",
        "colorama",
        "selenium",
        "sqlalchemy",
        "sqlalchemy_utils",
    ],
    entry_points="""
        [console_scripts]
        kultur=kultur.cli:main
    """,
)
