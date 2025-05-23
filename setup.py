from setuptools import setup, find_packages

setup(
    name="blog-platform",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.12",
        "uvicorn>=0.34.0",
        "motor>=3.3.2",
        "pymongo>=4.6.2",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.9",
        "bcrypt>=4.1.2",
        "python-slugify>=8.0.4",
        "pydantic>=2.10.6",
        "pydantic-settings>=2.8.1",
    ],
    python_requires=">=3.8",
) 