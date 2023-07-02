
from .operators import register_operators, unregister_operators
from .props import register_props, unregister_props
from .panels import register_panels, unregister_panels

def register_probes():
    register_operators()
    register_props()
    register_panels()

def unregister_probes():
    unregister_operators()
    unregister_props()
    unregister_panels()
