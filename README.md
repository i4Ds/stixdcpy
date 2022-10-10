
# stixdcpy
stixdcpy is a python package that facilitates access and analysis of STIX data. It provides APIs to query and download data from STIX data center (https://datacenter.stix.i4ds.net/) and s a set of tools for visualizing data and performing common analysis tasks.  With stixdcpy, users can query and download the following types of data from STIX data center:

- Quick-look light curves
- Housekeeping data
- Science data
- Energy calibration data
- Auxilary data
- STIX solar flare list



# Installation


```sh
pip install git+https://github.com/i4ds/stixdcpy.git
```
You may also need to install the following libraries:
```sh
pip install numpy matplotlib pandas astropy joblib
```

# Tutorial and documentation

- [Tutorial](https://github.com/i4ds/stixdcpy/blob/master/examples/tutorial.ipynb)
- [Try stixdcpy on Google Colab](https://colab.research.google.com/drive/17fQfbWjL0s0TpblbPL1Ysy_zFXj40FBf?usp=sharing)
- [Documentation](https://drhlxiao.github.io/stixdcpy/)


# Reporting Issues and Contributing
Open an issue on GitHub to report a problem. Pull requests welcome.

#  Cite this work
If you use the stixdcpy in your research and publications, we would definitely appreciate an appropriate acknowledgment and citation! We suggest the following BibTex:
```latex
@software{hualin_xiao_2022_7180433,
  author       = {Hualin Xiao and
                  Säm Krucker and
                  Lastufka Erica and
                  William Setterberg},
  title        = {{stixdcpy –  a python package that facilitates 
                   access and analysis of STIX data}},
  month        = oct,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v2.0},
  doi          = {10.5281/zenodo.7180433},
  url          = {https://doi.org/10.5281/zenodo.7180433}
}
```
