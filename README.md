
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7180433.svg)](https://doi.org/10.5281/zenodo.7180433)
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



#  Cite this work
If you use the stixdcpy in your research and publications, we would definitely appreciate an appropriate acknowledgment and citation! We suggest the following BibTex:
```latex
@misc{https://doi.org/10.48550/arxiv.2302.00497,
  doi = {10.48550/ARXIV.2302.00497},
  
  url = {https://arxiv.org/abs/2302.00497},
  
  author = {Xiao, Hualin and Maloney, Shane and Krucker, Säm and Dickson, Ewan and Massa, Paolo and Lastufka, Erica and Battaglia, Andrea Francesco and Etesi, Laszlo and Hochmuth, Nicky and Schuller, Frederic and Ryan, Daniel F. and Limousin, Olivier and Collier, Hannah and Warmuth, Alexander and Piana, Michele},
  
  keywords = {Solar and Stellar Astrophysics (astro-ph.SR), Instrumentation and Methods for Astrophysics (astro-ph.IM), FOS: Physical sciences, FOS: Physical sciences},
  
  title = {The data center for the X-ray spectrometer/imager STIX onboard Solar Orbiter},
  
  publisher = {arXiv},
  
  year = {2023},
  
  copyright = {Creative Commons Attribution 4.0 International}
}

```
# Reporting Issues and Contributing
Open an issue on GitHub to report a problem. Pull requests welcome.
