#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 09:41:05 2021

@author: carlos
"""

''' DESCARGA DE LA BIBLIOTECA '''
%matplotlib inline
!mkdir v002
!mkdir images
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/v002/Agent.py' -O v002/Agent.py
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/v002/Enviroment.py' -O v002/Enviroment.py
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/v002/__init__.py' -O v002/__init__.py
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/v002/Enviroment_with_agents.py' -O v002/Enviroment_with_agents.py
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/v002/InOut_Simple_Laberinth.py' -O v002/InOut_Simple_Laberinth.py
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/images/PixelNoTomato.bmp' -O images/PixelNoTomato.bmp
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/images/PixelTomato.bmp' -O images/PixelTomato.bmp
!wget 'https://github.com/cgarcia-UCO/AgentSurvival/raw/main/images/face1_borders.bmp' -O images/face1_borders.bmp

import time
from v002 import *
from v002.Agent import create_agent


''' DEFINICIÓN DE MI AGENTE '''
agent_name = 'YO!'

def move(self):
  # TODO define aquí dentro tu función. Lo siguiente es un ejemplo que deberías reemplazar con tu código
  for i in range(3):
    self.turn_right()
    self.move_forward()
    self.move_forward()
    
    
''' PRUEBA VISUAL'''
lb1 = InOut_Simple_Laberinth(7, plot_run='always', move_protection=False)
lb1.create_agent(agent_name, move)
lb1.run()



''' PRUEBA 'RÁPIDA' SOBRE 200 LABERINTOS OFFLINE '''
from tqdm import tqdm
num_runs = 200
num_success =  0

for _ in tqdm(range(num_runs)):
  lb1 = InOut_Simple_Laberinth(13, plot_run='never')
  lb1.create_agent(agent_name, move)
  winner = lb1.run()

  if winner is not None:
    num_success += 1

print("\n\nEncontraste la salida en", num_success, "ocasiones de", num_runs)

!rm -r v002 images
