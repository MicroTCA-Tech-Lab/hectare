import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

from hectare import __version__

setuptools.setup(
    name="hectare",
    version=__version__,
    author="Jan Marjanovic (DESY)",
    author_email="jan.marjanovic@desy.de",
    description="VHDL generator from SystemRDL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://techlab.desy.de",
    packages=setuptools.find_packages(include=['hectare', 'hectare.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'hectare=hectare.hectare:main',
        ],
    },
    install_requires=required,
    python_requires='>=3.5',
    keywords='systemrdl fpga vhdl axi registers',
)
