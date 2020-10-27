from distutils.core import setup

setup(
    name='python-upbit',
    packages=['python-upbit'],
    version='0.1',
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='A python wrapper for UPBit',
    author='Jungwoo Song',
    author_email='timepercent24@gmail.com',
    url='https://github.com/user/reponame',  # Provide either the link to your github or to your website
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    keywords=['upbit', 'pyupbit', 'cryptocurrency', 'api wrapper'],  # Keywords that define your package best
    install_requires=[
        'requests',
        'pyjwt'
    ],
    test_require=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
