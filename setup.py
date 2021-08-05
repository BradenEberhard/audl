import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="audl",
    version="1.0.1",
    author="yukikongju",
    author_email="yukikongju@outlook.com",
    description="Unofficial audl api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yukikongju/audl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "audl"},
    packages=setuptools.find_packages(where="audl"),
    python_requires=">=3.6",
)
