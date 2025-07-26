from setuptools import setup, find_packages

setup(
    name="telegram-anonymous-channel-bot",
    version="1.0.0",
    description="Comprehensive Telegram bot for anonymous channel management with Persian language support",
    author="Developer",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)