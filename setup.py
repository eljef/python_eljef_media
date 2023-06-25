# -*- coding: UTF-8 -*-
"""Setup script"""

from setuptools import setup

setup(
    author='Jef Oliver',
    author_email='jef@eljef.me',
    description='Various media utilities written by Jef Oliver',
    install_requires=['eljef-core>=2023.06.1', 'mutagen', 'Pillow', 'rgain3'],
    license='0BSD',
    name='eljef-media',
    packages=['eljef.media', 'eljef.media.cli', 'eljef.media.lib'],
    python_requires='>=3.8',
    url='https://eljef.dev/python/eljef_media',
    version='2023.06.3',
    entry_points={
        'console_scripts': [
            'ej-beet-flac = eljef.media.cli.__beet_flac_main__:cli_main',
            'ej-comic-fix = eljef.media.cli.__comic_fix_main__:cli_main',
            'ej-mp3-fix = eljef.media.cli.__mp3_fix_main__:cli_main',
            'ej-mp3-tag-dump = eljef.media.cli.__mp3_dump_tags_main__:cli_main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
    ]
)
