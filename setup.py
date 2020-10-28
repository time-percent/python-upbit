from setuptools import setup

import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='python-upbit',
    packages=['upbit'],
    version='0.1',
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='A python wrapper for UPBit',
    long_description=long_description,
    author='Jungwoo Song',
    author_email='timepercent24@gmail.com',
    url='https://github.com/user/reponame',  # Provide either the link to your github or to your website
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    keywords=['upbit', 'crypto', 'bitcoin'],  # Keywords that define your package best
    install_requires=[
        'requests',
        'pyjwt'
    ],
    test_requires=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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
