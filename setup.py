from setuptools import setup

import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='python-upbit-timepercent24',
    packages=['upbit'],
    version='0.1.0',
    license='MIT',
    description='A python wrapper for UPBit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jungwoo Song',
    author_email='timepercent24@gmail.com',
    url='https://github.com/time-percent/python-upbit',
    keywords=['upbit', 'crypto', 'bitcoin'],
    install_requires=[
        'requests',
        'pyjwt'
    ],
    test_requires=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/time-percent/python-upbit/issues',
        'Source': 'https://github.com/time-percent/python-upbit/'
    }
)
