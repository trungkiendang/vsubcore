from setuptools import setup, find_packages

setup(
    name="vsubcore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "ffmpy",
    ],
    entry_points={
        "console_scripts": [
            "vsub-nolog=vsubcore.vsub_nolog:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A speech recognition tool that converts video/audio to text and generates SRT subtitles",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/trungkiendang/vsubcore",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
) 