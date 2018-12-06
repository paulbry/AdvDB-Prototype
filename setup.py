# system
import setuptools

setuptools.setup(
    name="union-prototype",
    version="0.1.0",
    author="?",
    packages=[
        "union_prototype"
    ],
    include_package_date=False,
    url="https://github.com/paulbry/AdvDB-Prototype",
    description="Advance Database prototype project",
    install_requires=[
        'termcolor',
        'flask',
        'flask_restful',
        'google-cloud-storage',
        'pymongo',
        'boto3'
    ],
    entry_points={
        'console_scripts': [
            'union-prototype = union_prototype.__main__:main'
        ]
    }
)