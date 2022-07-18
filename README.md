# What is stixdcpy
stixdcpy is a python package that facilitates access and analysis of STIX data. It provides APIs to query and download data from STIX data center (https://datacenter.stix.i4ds.net/) and s a set of tools for visualizing data and performing common analysis tasks.  With stixdcpy, users can query and download the following types of data from STIX data center:

- Quick-look light curves
- Housekeeping data
- Science data
- Energy calibration data
- Auxilary data
- STIX solar flare list



# Installation

Install from pypi:
```sh
pip install stixdcpy
```
It can be also installed from stixdcpy github repository:

```sh
pip install git+https://github.com/drhlxiao/stixdcpy.git
```
You may also need to install the following python libraries:
```sh
pip install numpy matplotlib pandas astropy joblib
```

# Tutorial and documentation

- [Tutorial](https://github.com/drhlxiao/stixdcpy/blob/master/examples/tutorial.ipynb)
- [Try stixdcpy on Google Colab](https://colab.research.google.com/drive/17fQfbWjL0s0TpblbPL1Ysy_zFXj40FBf?usp=sharing)
- [Documentation](https://drhlxiao.github.io/stixdcpy/)

# Reporting Issues and Contributing
Open an issue on GitHub to report a problem. Pull requests welcome.

# Citing stixdcpy
If you use stixdcpy in your work, please use the following citation,

@software{hualin_xiao_2022_6408689,
  author       = {Hualin Xiao},
  title        = {stixdcpy - a python package for accessing and analyzing STIX data},
  month        = apr,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v1.0},
  doi          = {10.5281/zenodo.6408689},
  url          = {https://doi.org/10.5281/zenodo.6408689}
}
