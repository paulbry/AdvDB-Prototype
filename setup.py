import setuptools

setuptools.setup(
    name="union-prototype",
    version="0.1.0",
    author="?",
    packages=[
        "advdb_prototype"
    ],
    include_package_date=False,
    url="https://github.com/paulbry/AdvDB-Prototype",
    description="Advance Database prototype project",
    install_requires=[
        'termcolor',
        'flask',
        'flask_restful'
    ],
    entry_points={
        'console_scripts': [
            'union-prototype = union_protoype.__main__:main'
        ]
    }
)