# -*- coding: UTF-8 -*-
"""Setup script"""

from setuptools import setup

setup(
    author='Jef Oliver',
    author_email='jef@eljef.me',
    description='Various media utilities written by Jef Oliver',
    install_requires=['eljef-core>=1.6.0', 'mutagen', 'Pillow', 'rgain3'],
    license='LGPLv2.1',
    name='eljef_media',
    packages=['eljef.media', 'eljef.media.cli', 'eljef.media.lib'],
    python_requires='>=3.8',
    url='https://github.com/eljef/python_eljef_media',
    version='0.4.0',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'ej-comic-fix = eljef.media.cli.__comic_fix_main__:cli_main',
            'ej-mp3-fix = eljef.media.cli.__mp3_fix_main__:cli_main',
            'ej-mp3-tag-dump = eljef.media.cli.__mp3_dump_tags_main__:cli_main'
        ]
    },
)
