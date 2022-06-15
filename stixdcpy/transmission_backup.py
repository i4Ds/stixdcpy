from collections import OrderedDict
from functools import partial

import astropy.units as u
import numpy as np
from astropy.table.table import Table
from roentgen.absorption.material import Compound, MassAttenuationCoefficient, Material

#from stixcore.config.reader import read_energy_channels

__all__ = ['Transmission']

MIL_SI = 0.0254 * u.mm

# TODO move to configuration files
COMPONENTS = OrderedDict([
    ('front_window', [('solarblack', 0.005 * u.mm), ('be', 2 * u.mm)]),
    ('rear_window', [('be', 1 * u.mm)]),
    ('grid_covers', [('kapton', 4 * 2 * MIL_SI)]),
    ('dem', [('kapton', 2 * 3 * MIL_SI)]),
    ('attenuator', [('al', 0.6 * u.mm)]),
    ('mli', [('al', 1000 * u.angstrom), ('kapton', 3 * MIL_SI),
             ('al', 40 * 1000 * u.angstrom), ('mylar', 20 * 0.25 * MIL_SI),
             ('pet', 21 * 0.005 * u.mm), ('kapton', 3 * MIL_SI),
             ('al', 1000 * u.angstrom)]),
    ('calibration_foil', [('al', 4 * 1000 * u.angstrom),
                          ('kapton', 4 * 2 * MIL_SI)]),
    ('dead_layer', [('te_o2', 392 * u.nm)]),
])

MATERIALS = OrderedDict([
    ('al', ({
        'Al': 1.0
    }, 2.7 * u.g / u.cm**3)),
    ('be', ({
        'Be': 1.0
    }, 1.85 * u.g / u.cm**3)),
    ('kapton', ({
        'H': 0.026362,
        'C': 0.691133,
        'N': 0.073270,
        'O': 0.209235
    }, 1.43 * u.g / u.cm**3)),
    ('mylar', ({
        'H': 0.041959,
        'C': 0.625017,
        'O': 0.333025
    }, 1.38 * u.g / u.cm**3)),
    ('pet', ({
        'H': 0.041960,
        'C': 0.625016,
        'O': 0.333024
    }, 1.370 * u.g / u.cm**3)),
    ('solarblack_oxygen', ({
        'H': 0.002,
        'O': 0.415,
        'Ca': 0.396,
        'P': 0.187
    }, 3.2 * u.g / u.cm**3)),
    ('solarblack_carbon', ({
        'C': 0.301,
        'Ca': 0.503,
        'P': 0.195
    }, 3.2 * u.g / u.cm**3)),
    ('te_o2', ({
        'Te': 0.7995088158691722,
        'O': 0.20049124678825841
    }, 5.670 * u.g / u.cm**3)),
])

#    'Channel Number', 'Channel Edge', 'Energy Edge ', 'Elower', 'Eupper ',
#    'BinWidth', 'dE/E', 'QL channel'
default_energy_bins = [['0', '0', '0', '0', '4', '4', '2', 'n/a'],
                       ['1', '1', '4', '4', '5', '1', '0.222', '0'],
                       ['2', '2', '5', '5', '6', '1', '0.182', '0'],
                       ['3', '3', '6', '6', '7', '1', '0.154', '0'],
                       ['4', '4', '7', '7', '8', '1', '0.133', '0'],
                       ['5', '5', '8', '8', '9', '1', '0.118', '0'],
                       ['6', '6', '9', '9', '10', '1', '0.105', '0'],
                       ['7', '7', '10', '10', '11', '1', '0.095', '1'],
                       ['8', '8', '11', '11', '12', '1', '0.087', '1'],
                       ['9', '9', '12', '12', '13', '1', '0.08', '1'],
                       ['10', '10', '13', '13', '14', '1', '0.074', '1'],
                       ['11', '11', '14', '14', '15', '1', '0.069', '1'],
                       ['12', '12', '15', '15', '16', '1', '0.065', '2'],
                       ['13', '13', '16', '16', '17', '1', '0.061', '2'],
                       ['14', '14', '18', '18', '20', '2', '0.105', '2'],
                       ['15', '15', '20', '20', '22', '2', '0.095', '2'],
                       ['16', '16', '22', '22', '25', '3', '0.128', '2'],
                       ['17', '17', '25', '25', '28', '3', '0.113', '3'],
                       ['18', '18', '28', '28', '32', '4', '0.133', '3'],
                       ['19', '19', '32', '32', '36', '4', '0.118', '3'],
                       ['20', '20', '36', '36', '40', '4', '0.105', '3'],
                       ['21', '21', '40', '40', '45', '5', '0.118', '3'],
                       ['22', '22', '45', '45', '50', '5', '0.105', '3'],
                       ['23', '23', '50', '50', '56', '6', '0.113', '4'],
                       ['24', '24', '56', '56', '63', '7', '0.118', '4'],
                       ['25', '25', '63', '63', '70', '7', '0.105', '4'],
                       ['26', '26', '70', '70', '76', '6', '0.082', '4'],
                       ['27', '27', '76', '76', '84', '8', '0.1', '4'],
                       ['28', '28', '84', '84', '100', '16', '0.174', '4'],
                       ['29', '29', '100', '100', '120', '20', '0.182', '4'],
                       ['30', '30', '120', '120', '150', '30', '0.222', '4'],
                       [
                           '31', '31', '150', '150', 'maxADC', 'n/a', 'n/a',
                           'n/a'
                       ], ['', '32', 'max ADC', '', '', '', '', '']]


def float_def(value, default=np.inf):
    """Parse the value into a float or return the default value.

    Parameters
    ----------
    value : `str`
        the value to parse
    default : `double`, optional
        default value to return in case of pasring errors, by default numpy.inf

    Returns
    -------
    `double`
        the parsed value
    """
    try:
        return float(value)
    except ValueError:
        return default


def int_def(value, default=0):
    """Parse the value into a int or return the default value.

    Parameters
    ----------
    value : `str`
        the value to parse
    default : `int`, optional
        default value to return in case of pasring errors, by default 0

    Returns
    -------
    `int`
        the parsed value
    """
    try:
        return int(value)
    except ValueError:
        return default


# TODO get file from config
'''
class EnergyChannel:
    """Represent a STIX energy channel.

    Attributes
    ----------
    channel_edge : ´int´
        chanel idx
    energy_edge : ´int´
        edge on energy axis
    e_lower : ´float´
        start of the energy band in keV
    e_upper : ´float´
        end of the energy band in keV
    bin_width : ´float´
        width of the energy band in keV
    dE_E : ´float´
        TODO
    """

    def __init__(self, *, channel_edge, energy_edge, e_lower, e_upper, bin_width, dE_E):
        self.channel_edge = channel_edge
        self.energy_edge = energy_edge
        self.e_lower = e_lower
        self.e_upper = e_upper
        self.bin_width = bin_width
        self.dE_E = dE_E

    def __repr__(self):
        return f'{self.__class__.__name__}(channel_edge={self.channel_edge}, ' +\
               f'energy_edge={self.energy_edge}, e_lower={self.e_lower}, e_upper={self.e_upper},' +\
               f' bin_width={self.bin_width}, dE_E={self.dE_E})'
def read_energy_channels(energy_bin_config=default_energy_bins):
    """Read the energy channels from the configuration file.

    Parameters
    ----------
    path : `pathlib.Path`
        path to the config file

    Returns
    -------
    `dict`
        set of `EnergyChannel` accessible by index
    """
    energy_channels = dict()
    if energy_bin_config:
        for row in energy_bin_config:
        
            idx = int_def(row[0], -1)
            if idx == -1:
                continue
            energy_channels[idx] = EnergyChannel(
                channel_edge=int_def(row[1]),
                energy_edge=int_def(row[2]),
                e_lower=float_def(row[3]),
                e_upper=float_def(row[4]),
                bin_width=float_def(row[5]),
                dE_E=float_def(row[6])
            )

    return energy_channels

#ENERGY_CHANNELS = read_energy_channels(default_energy_bins)
'''


class Transmission:
    """
    Calculate the energy dependant transmission of X-ray through the instrument
    """
    def __init__(self, solarblack='solarblack_carbon'):
        """
        Create a new instance of the transmission with the given solar black composition.

        Parameters
        ----------

        solarblack : `str` optional
            The SolarBlack composition to use.
        """
        if solarblack not in ['solarblack_oxygen', 'solarblack_carbon']:
            raise ValueError(
                "solarblack must be either 'solarblack_oxygen' or "
                "'solarblack_carbon'.")

        self.solarblack = solarblack
        self.materials = MATERIALS
        self.components = COMPONENTS
        self.components = dict()

        for name, layers in COMPONENTS.items():
            parts = []
            for material, thickness in layers:
                if material == 'solarblack':
                    material = self.solarblack
                mass_frac, den = MATERIALS[material]
                if material == 'al':
                    thickness = thickness * 0.8
                parts.append(
                    self.create_material(name=material,
                                         fractional_masses=mass_frac,
                                         thickness=thickness,
                                         density=den))
            self.components[name] = Compound(parts)

    def get_transmission(self, energies, attenuator=False):
        """
        Get the transmission for each detector at the center of the given energy bins.

        If energies are not supplied will evaluate at standard science energy channels

        Parameters
        ----------
        energies : `astropy.units.Quantity`, optional
            The energies to evaluate the transmission
        attenuator : `bool`, optional
            True for attenuator in X-ray path, False for attenuator not in X-ray path

        Returns
        -------
        `astropy.table.Table`
            Table containing the transmission values for each energy and detector
        """
        base_comps = [
            self.components[name] for name in [
                'front_window', 'rear_window', 'dem', 'mli',
                'calibration_foil', 'dead_layer'
            ]
        ]

        #if energies is None:
        energies = energies * u.keV
        #    self.energies = [ENERGY_CHANNELS[i].e_lower for i in range(1, 32)] * u.keV

        if attenuator:
            base_comps.append(self.components['attenuator'])

        base = Compound(base_comps)
        base_trans = base.transmission(energies)

        fine = Compound(base_comps + [self.components['grid_covers']])
        fine_trans = fine.transmission(energies)

        # TODO need to move to configuration db
        fine_grids = np.array([11, 13, 18, 12, 19, 17]) - 1
        detector_transmission = Table()
        # transmission['sci_channel'] = range(1, 31)
        detector_transmission['energies'] = energies
        for i in range(32):
            name = f'det-{i}'
            if np.isin(i, fine_grids):
                detector_transmission[name] = fine_trans
            else:
                detector_transmission[name] = base_trans
        return detector_transmission

    def get_detector_transmission(self,
                                  detector_id,
                                  energy_bins,
                                  attenuator=False):
        '''
            get transmission for detector
            Arguments
            ---------
            detector:  ranges from 0...31 
            energy_bins:   32 x 2 array like [[e_bin_0_low, ebin_0_up], ...[]]
            Returns
            --------
            transmission for the energy bins
            
        '''
        base_comps = [
            self.components[name] for name in [
                'front_window', 'rear_window', 'dem', 'mli',
                'calibration_foil', 'dead_layer'
            ]
        ]

        if attenuator:
            base_comps.append(self.components['attenuator'])

        fine_grids = [10, 12, 17, 11, 18, 16]

        if detector_id in fine_grids:
            comp = Compound(base_comps + [self.components['grid_covers']])
        else:
            comp = Compound(base_comps)

        ebins_1d = energy_bins.reshape(-1) * u.keV
        #convert energy bin ranges to 1d
        det_trans = comp.transmission(ebins_1d)
        mean_trans = np.mean(det_trans.reshape((-1, 2)), axis=1)
        #calculate mean energy transmission factors for energy bins
        return mean_trans

    def get_transmission_by_component(self):
        """
        Get the contributions to the total transmission by broken down by component.

        Returns
        -------
        `dict`
            Entries are Compounds for each component
        """
        return self.components

    def get_transmission_by_material(self):
        """
        Get the contribution to the transmission by total thickness for each material.

        Layers of the same materials are combined to return one instance with the total thickness.

        Returns
        -------
        `dict`
            Entries are meterials with the total thickness for that material.
        """
        material_thickness = dict()
        for name, layers in COMPONENTS.items():
            for material_name, thickness in layers:
                if material_name == 'solarblack':
                    material_name = self.solarblack
                if material_name in material_thickness.keys():
                    material_thickness[material_name] += thickness.to('mm')
                else:
                    material_thickness[material_name] = thickness.to('mm')
        res = {}
        for name, thickness in material_thickness.items():
            frac_mass, density = self.materials[name]
            mat = self.create_material(name=name,
                                       fractional_masses=frac_mass,
                                       density=density,
                                       thickness=thickness)
            res[name] = mat

        return res

    @classmethod
    def create_material(cls,
                        name=None,
                        fractional_masses=None,
                        thickness=None,
                        density=None):
        """
        Create a new material given the composition and fractional masses.

        Parameters
        ----------
        name : `str`
            Name of the meterial
        fractional_masses : `dict`
            The element and fractional masses of the material e.g. `{'H': 0.031, 'O': 0.969}`
        thickness : `astropy.units.Quantity`
            Thickness of the material
        density : `astropy.units.Quantity`
            Density of the material

        Returns
        -------
        `roentgen.absorption.material.Material`
            The material
        """
        material = Material('h', thickness, density)
        material.name = name
        # probably don't need this
        material.density = density

        # TODO remove in favour of upstream fix when completed
        #  see https://github.com/ehsteve/roentgen/issues/26
        def func(composition, e):
            return sum([
                MassAttenuationCoefficient(element).func(e) * frac_mass
                for element, frac_mass in composition.items()
            ])

        material_func = partial(func, fractional_masses)

        material.mass_attenuation_coefficient.func = material_func
        return material


"""
def generate_transmission_tables():
    from datetime import datetime
    cur_date = datetime.now().strftime('%Y%m%d')
    datetime.now().strftime('%Y%m%d')
    trans = Transmission()
    norm_sci_energies = trans.get_transmission()
    norm_sci_energies.write(f'stix_transmission_sci_energies_{cur_date}.csv')
    norm_high_res = trans.get_transmission(energies=energies)
    norm_high_res.write(f'stix_transmission_highres_{cur_date}.csv')

    comps = trans.get_transmission_by_component()

    comps_sci_energies = Table([c.transmission(trans.energies) for c in comps.values()],
                               names=[k for k in comps.keys()])
    comps_sci_energies['energy'] = trans.energies
    comps_sci_energies.write(f'stix_transmission_by_component_sci_energies_{cur_date}.csv')

    comps_highres = Table([c.transmission(energies) for c in comps.values()],
                          names=[k for k in comps.keys()])
    comps_highres['energy'] = energies
    comps_highres.write(f'stix_transmission_by_component_highres_{cur_date}.csv')

generate_transmission_tables()
"""


def get_detector_absorption(energies=None):
    mass_fraction = {'Te': 0.531644, 'Cd': 0.4683554}
    desity = 5.85 * u.g / u.cm**3
    thickness = 1 * u.mm
    material = Transmission.create_material(name='cdte',
                                            fractional_masses=mass_fraction,
                                            thickness=thickness,
                                            density=density)
    if energies is None:
        energies = np.linspace(2, 150, 1001)
        energies = energies * u.keV
    absorption = material.absorption(energies)
    print(absorption)


#def get_transmission(energies):
#    return trans.get_transmission(energies)
if __name__ == '__main__':
    energies = np.linspace(2, 150, 1001)
    tr = Transmission()
    t = tr.get_transmission(energies)
    t.pprint()
    print(t['det-0'][0])
