from setuptools import setup, find_packages

setup(
    name='stixdcpy',
    description='STIX data center APIs and data analysis tools',
    version='2.1',
    author='Hualin Xiao',
    author_email='hualin.xiao@fhnw.ch',
    long_description=open('README.md').read(),
    install_requires=['numpy', 'requests', 'python-dateutil',
                      'astropy', 'sunpy','matplotlib','tqdm','roentgen'],
    long_description_content_type='text/markdown',
    #packages=find_packages(where='stixdcpy'),
    url='https://github.com/drhlxiao/stixdcpy',
    packages=['stixdcpy'],
    python_requires='>=3.6'
)
