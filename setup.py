from setuptools import setup
import json


with open("metadata.json") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_northeuralex",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_northeuralex"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["northeuralex=lexibank_northeuralex:Dataset"]},
    install_requires=["pylexibank"],
    extras_require={"test": ["pytest-cldf"]},
)
