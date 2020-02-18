from setuptools import setup

setup(
    name='matlab-documenter',
    version='0.1',
    py_modules=['mdoc'],
    include_package_data=True,
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        mdoc=mdoc:cli
    ''',
)
