from setuptools import setup, find_packages

setup(
    name="res_sat",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "res_sat=main:main",
        ],
    },
)