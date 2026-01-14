from setuptools import setup, find_packages

setup(
    name="card-signal-board",
    version="0.1.0",
    description="Card Signal Board API - FastAPI microservice",
    author="Mohamed Bouafif",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.0",
        "pydantic[email]==2.5.0",
        "httpx==0.25.2",
        "prometheus-client==0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==7.0.0",
            "black==23.12.0",
            "flake8==6.1.0",
            "bandit==1.7.5",
        ],
    },
)
