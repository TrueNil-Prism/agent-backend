import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agent-backend",
    version="0.0.1",
    author="Kartik Lakshminarayanan",
    author_email="kartik@truenil.io",
    description="Agent Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orgs/TrueNil-Prism/agent-backend",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.11",
)