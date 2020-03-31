import sys
from setuptools import setup, find_packages

setup(name="meshcat_ros_fileserver",
    version="0.0.1",
    description="File server for Meshcat",
    #url="https://github.com/rdeits/meshcat-python",
    #download_url="https://github.com/rdeits/meshcat-python/archive/v0.0.15.tar.gz",
    author="Vladimir Ivan",
    author_email="v.ivan@ed.ac.uk",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    #test_suite="meshcat",
    entry_points={
        "console_scripts": [
            "meshcat-ros-fileserver=meshcat_ros_fileserver.server:main"
        ]
    },
    install_requires=[
      "tornado >= 4.0.0" if sys.version_info >= (3, 0) else "tornado >= 4.0.0, < 6.0"
    ],
    zip_safe=False,
    include_package_data=True
)
