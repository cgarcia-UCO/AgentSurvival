try:
    from IPython import get_ipython

    if get_ipython().__class__.__name__ != 'NoneType':
        from IPython import display
        i_am_in_interatcive = True
        import pylab as pl
    else:
        import matplotlib.pyplot as pl
        i_am_in_interatcive = False
except:
    import matplotlib.pyplot as pl
    i_am_in_interatcive = False

from .Agent import Agent
from .Enviroment_with_agents import Enviroment_with_agents
from .Enviroment import Enviroment
import numpy as np