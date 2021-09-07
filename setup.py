try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='sdcpy',
    description='STIX data center python tools',
    version='1.0.0',
    packages=setuptools.find_packages(),
    long_description=open('README.md').read(),
    install_requires=['numpy', 'requests', 'python-dateutil',
                      'astropy', 'sunpy','matplotlib','tqdm'],
    long_description_content_type='text/markdown',
    python_requires='>=3.6'
)
