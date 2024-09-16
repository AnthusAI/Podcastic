from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="podcastic",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to generate audio podcasts from SSML files using OpenAI or Eleven Labs TTS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/podcastic",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "openai",
        "pydub",
        "pyyaml",
        "requests",
        "python-dotenv",
        "rich",
        "langchain",
        "langchain-community",
        "elevenlabs",
        "langchain-openai",
        "pytest",
        "pytest-watch"
    ],
    entry_points={
        "console_scripts": [
            "podcastic=podcastic.podcastic:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
    license_files=("LICENSE",),
)