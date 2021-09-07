from setuptools import setup, find_packages

setup(
    name='stixdcpy',
    description='STIX data center python tools',
    version='1.0.0',
    author='Hualin Xiao',
    author_email='hualin.xiao@fhnw.ch',
    long_description=open('README.md').read(),
    install_requires=['numpy', 'requests', 'python-dateutil',
                      'astropy', 'sunpy','matplotlib','tqdm'],
    long_description_content_type='text/markdown',
    package_dir={"":"stixdcpy"},
    packages=find_packages(where='stixdcpy'),
    python_requires='>=3.6'
)
