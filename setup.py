from distutils.core import setup

import lowerpines

setup(
    name='lowerpines',
    packages=['lowerpines', 'lowerpines.endpoints'],
    version=lowerpines.VERSION,
    description='Library wrapper for GroupMe API',
    requires=['requests'],
    license='GNU Lesser General Public License v3 (LGPLv3)',
    author='Jonathan Janzen',
    author_email='jjjonjanzen@gmail.com',
    url='https://github.com/bigfootjon/lowerpines',
    download_url='https://github.com/bigfootjon/lowerpines/tarball/' + lowerpines.VERSION,
    keywords=['api', 'GroupMe'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Chat',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
