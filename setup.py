import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minecraft-manager",
    version="0.1.0",
    author="Galen Guyer",
    author_email="galen@galenguyer.com",
    description="a command line tool for creating minecraft servers with a start script and optional systemd file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/galenguyer/minecraft-manager",
    packages=setuptools.find_packages(),
    entry_points={
		'console_scripts':[
			'mcm = mcm:main',
		],
	},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux"
        "Environment :: Console",
    ],
    python_requires='>=3.6',
)