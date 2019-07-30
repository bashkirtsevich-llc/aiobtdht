from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="aio-btdht",
    version="0.0.4",
    description="Asyncio Bittorrent DHT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python"],
    keywords="Async Bittorrent-DHT DHT",
    author="D.Bashkirtsevich",
    author_email="bashkirtsevich@gmail.com",
    url="https://github.com/bashkirtsevich-llc/aiobtdht",
    license="GPL3 License",
    include_package_data=True,
    zip_safe=True,
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6.*",
    install_requires=[
        "aio-krpc-server==0.0.4"
    ]
)