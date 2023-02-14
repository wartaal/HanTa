import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HanTa",
    version="1.1.0",
    author="Christian Wartena",
    author_email="Christian.Wartena@hs-hannover.de",
    description="Hannover Tagger: Morphological Analysis and POS Tagging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wartaal/HanTa",
    packages=setuptools.find_packages(),
    package_data = {'HanTa': ['*.pgz']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: Dutch",
        "Natural Language :: English",
        "Natural Language :: German",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers"
    ],
)
