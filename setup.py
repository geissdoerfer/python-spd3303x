import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

requirements = ["numpy", "pyvisa-py", "click", "python-vxi11"]

setup(
    name="spd3303x",
    version="1.0.0",
    description="Python API for SigLent SPD3303X",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=["spd3303x"],
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
    ],
    install_requires=requirements,
    author="Kai Geissdoerfer",
    author_email="kai.geissdoerfer@tu-dresden.de",
    setup_requires=["pytest-runner"],
    tests_require=["pytest>=3.9"],
    entry_points={"console_scripts": ["spd-ctrl=spd3303x.cli:cli"]},
)
