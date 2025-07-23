from setuptools import setup, find_packages

setup(
    name="patent-similarity-search",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "neo4j",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "langchain",
        "langchain-community",
        "python-jose",
        "typing-extensions",
        "numpy"
    ],
)
