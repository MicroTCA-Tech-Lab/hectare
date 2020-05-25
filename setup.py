import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="hectare", # Replace with your own username
    version="0.1.0",
    author="Jan Marjanovic (DESY)",
    author_email="jan.marjanovic@desy.de",
    description="VHDL generator from SystemRDL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://techlab.desy.de",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    python_requires='>=3.5',
)
