from setuptools import setup, find_packages

setup(
    name='nseapi',
    version='0.1.0',
    description='A package for interacting with nseindia.com to retrieve market data',
    long_description='This package provides tools for interacting with the National Stock Exchange of India (NSE) website. It allows users to fetch various types of market data, including the current market status and historical equity bhavcopies.',
    long_description_content_type='text/markdown',
    author='kushgbisen',
    author_email='kushgbisen@gmail.com',
    url='https://github.com/kushgbisen/nseapi',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)
