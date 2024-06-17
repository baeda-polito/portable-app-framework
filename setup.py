"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/portable-app-framework
https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py
"""

import pathlib

from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
setup(
    name="PFB-Toolkit",
    version="0.1.6",
    description="Portable Framework for Building Applications - PFB-Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RobertoChiosa/portable-app-framework",
    author="Roberto Chiosa",
    author_email="roberto.chiosa@polito.it",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    include_package_data=True,
    package_data={
        "portable_app_framework": ["**/*.md", "**/*.rq", "**/*.ttl", "**/*.yaml"],
    },
    entry_points={
        "console_scripts": [
            "portable-app-framework=portable_app_framework:cli_entry_point",
        ],
    },
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    project_urls={
        "Bug Reports": "https://github.com/RobertoChiosa/portable-app-framework/issues",
        "Source": "https://github.com/RobertoChiosa/portable-app-framework/",
    },
)
