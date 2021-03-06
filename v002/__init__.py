try:
    from IPython import get_ipython

    if get_ipython().__class__.__name__ not in ['NoneType']:
        from IPython import display
        i_am_in_interatcive = True
        import pylab as pl
        pl.rcParams['figure.figsize'] = [13, 13]
        # print("INTERACTIVE")
    else:
        import matplotlib.pyplot as pl
        i_am_in_interatcive = False
        # print("NOT INTERACTIVE")
except:
    import matplotlib.pyplot as pl
    i_am_in_interatcive = False

# print("__INIT__ EXECUTED")

from .Agent import Agent
from .Enviroment_with_agents import Enviroment_with_agents
from .Enviroment import Enviroment
from .InOut_Simple_Laberinth import InOut_Simple_Laberinth, No_Walls_Laberinth
import numpy as np
