from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="verisigil",
    version="0.1.0",
    author="VeriSigil AI",
    author_email="info@verisigilai.com",
    description="Operational Admissibility Infrastructure for Autonomous Enterprise AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://verisigilai.com",
    project_urls={
        "Documentation": "https://verisigil-api-production.up.railway.app/docs",
        "Source":        "https://github.com/raheem-verisigil/verisigil-sdk",
        "Tracker":       "https://github.com/raheem-verisigil/verisigil-sdk/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],   # Zero dependencies — stdlib only
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "ai governance", "eu ai act", "runtime admissibility",
        "agent governance", "operational governance", "cryptographic audit",
        "verisigil", "ai compliance", "autonomous ai",
    ],
)
