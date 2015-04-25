

_var_wisdom = {
    'T2' : {
        'native_unit' : 'K',
        'colorbar_units' : ['C', 'F'],
        'colormap' : 'jet',
        'scale' : 'original'
      },
    'RH_FIRE' : {
        'native_unit' : '-',
        'colorbar_units' : ['-'],
        'colormap' : 'jet_r',
        'scale' : [0.0, 1.5]
      },
    'F_ROS' : {
       'native_unit' : 'm/s',
       'colorbar_units' : ['m/s', 'ft/s'],
       'colormap' : 'jet',
       'scale' : [0.0, 2.0],
      },
    'F_INT' : {
       'native_unit' : 'J/m/s^2',
       'colorbar_units' : ['J/m/s^2'],
       'colormap' : 'jet',
       'scale' : 'original'
    },
    'NFUEL_CAT' : {
       'native_unit' : 'fuel_type',
       'colorbar_units' : ['fuel_type'],
       'colormap' : 'jet',
       'scale' : 'original'
    },
    'ZSF' : {
       'native_unit' : 'm',
       'colorbar_units' : ['m','ft'],
       'colormap' : 'jet',
       'scale' : 'original'
    },
    'FMC_G' : {
       'native_unit' : '-',
       'colorbar_units' : ['-'],
       'colormap' : 'jet_r',
       'scale' : [0.0, 1.5]
    }
}

# contains functions to transform values from one unit to another in a simple format.
# it's a dictionary with keys in the form (from_unit, to_unit) and the value is a lambda
# that maps the value from <from_unit> to <to_unit>.
_units_wisdom = {
    ('K',   'C') : lambda x: x - 273.15,
    ('K',   'F') : lambda x: 9.0 / 5.0 * (x - 273.15) + 32,
    ('m/s', 'ft/s') : lambda x: 3.2808399 * x,
    ('m',   'ft') : lambda x: 3.2808399 * x,
    ('ft/s','m/s') : lambda x: x / 3.2808399,
    ('ft',  'm') : lambda x: x / 3.2808399
}



def get_wisdom(var_name):
    """Return rendering wisdom for the variable <var_name>."""
    return _var_wisdom[var_name]

def get_wisdom_variables():
    """Return the variables for which wisdom is available."""
    return _var_wisdom.keys()

def convert_value(unit_from, unit_to, value):
    # handle the simple case
    if unit_from == unit_to:
        return value

    func = _units_wisdom.get((unit_from, unit_to))
    if func is None:
        return None
    else:
        return func(value)



        

    

