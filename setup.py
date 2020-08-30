from setuptools import setup

setup(
    name='akari',
    url='https://github.com/shunjuu/Akari',
    author='Kyrielight',
    packages=['akari'],
    install_requires=[
        'ayumi @ git+https://github.com/shunjuu/Ayumi',
        'requests'
    ],
    version='0.1',
    license='MIT',
    description='Jikan.moe Userlist Wrapper.'
)