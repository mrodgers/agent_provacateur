from setuptools import setup, find_packages

setup(
    name="graphrag_mcp_py",
    version="1.0.0",
    description="GraphRAG MCP Server (Python Implementation)",
    author="Agent Provocateur Team",
    author_email="noreply@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.0",
        "python-multipart>=0.0.5"
    ],
    entry_points={
        "console_scripts": [
            "graphrag-mcp=graphrag_mcp_py.src.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)