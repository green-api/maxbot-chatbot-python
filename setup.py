from setuptools import setup, find_packages

with open("README.md", encoding="UTF-8") as file:
    long_description = file.read()

setup(
    name="maxbot-chatbot-python",
    version="1.1.0",
    description="Python SDK and Chatbot Framework for MAX API",
    long_description=long_description,
    author="Green-API",
    url="https://github.com/green-api/maxbot-chatbot-python",
    packages=find_packages(exclude=["examples*"]), 
    install_requires=[
        "maxbot-api-client-python>=1.1.2",
        "httpx>=0.24.0",
        "pydantic>=2.0.0"
    ],
    python_requires=">=3.12",
)
