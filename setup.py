"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/afdd-framework
https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py
"""

import pathlib

from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
setup(
    name="afdd-framework",
    version="0.1.0",
    description="Automated fault detection and diagnosis for HVAC systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/afdd-framework",
    author="Roberto Chiosa",
    author_email="roberto.chiosa@polito.it",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="fdd",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    project_urls={
        "Bug Reports": "https://github.com/RobertoChiosa/afdd-framework/issues",
        "Source": "https://github.com/RobertoChiosa/afdd-framework/",
    },
)
