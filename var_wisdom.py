

_var_wisdom = {
    'T2' : {
        'native_unit' : 'K',
        'colorbar_units' : ['C', 'F'],
        'colormap' : 'jet'
      },
    'RH_FIRE' : {
        'native_unit' : '-',
        'colorbar_units' : ['-'],
        'colormap' : 'jet_r'
      },
    'F_ROS' : {
       'native_unit' : 'm/s',
       'colorbar_units' : ['m/s'],
       'colormap' : 'jet'
      },
    'F_INT' : {
       'native_unit' : 'J/m/s^2',
       'colorbar_units' : ['J/m/s^2'],
       'colormap' : 'jet'
    }
}

# contains functions to transform values from one unit to another in a simple format.
# it's a dictionary with keys in the form (from_unit, to_unit) and the value is a lambda
# that maps the value from <from_unit> to <to_unit>.
_units_wisdom = {
    ('K', 'C') : lambda x: x - 273.15,
    ('K', 'F') : lambda x: 9.0 / 5.0 * (x - 273.15) + 32
}



def get_wisdom(var_name):
    """Return rendering wisdom for the variable <var_name>."""
    return _var_wisdom(var_name)

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



        

    

