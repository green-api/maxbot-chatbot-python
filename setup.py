from setuptools import setup, find_packages

setup(
    name="maxbot-chatbot-python",
    version="1.0.1",
    description="Python SDK and Chatbot Framework for MAX API",
    author="Green-API",
    packages=find_packages(exclude=["examples*"]), 
    install_requires=[
        "maxbot-api-client-python"
        "httpx",
        "pydantic"
    ],
    python_requires=">=3.8",
)