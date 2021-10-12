

'''
Esta clase tiene agentes (clase anterior) que se mueven en el laberinto. Los agentes tienen métodos para moverse hacia adelante
y para girar a ambos lados.

HECHO Cuando un agente hace una acción, el Laberinto debería comprobar si ha agotado el número de movimientos en su turno,
y así evitar que se intente hacer agentes tramposos. TODO Eso está hecho desde el agente, sin embargo, no está hecho
desde funciones de objetos. Por ejemplo, si se quisiese que comer un objeto consumiese un movimiento. Para ello,
de alguna forma debería hacer que la función de comer estuviese decorada con el agente que la invoca, de forma que
así también se podría comprobar el número de movimientos ejecutados.

HECHO el laberinto debería ser el que llamase a los agentes indicándoles que les toca y que deben realizar un movimiento (hasta tres por turno, por ejemplo).

HECHO quizás la solución sea definir los Agentes dentro de la clase Laberinth, y que el create_agent reciba la función de movimiento.
Así, toda la información de los agentes está "protegida" dentro del laberinto. Esto no impide que el estudiante defina sus funciones
dentro de clases que ellos se creen, pero "protege" la información de los mismos dentro del Laberinto.

TODO quitar por defecto la entrada y salida del laberinto
TODO definir como subclase simple el problema de entrar y salir del laberinto
TODO podríamos definir también el de llegar a un punto destino conocido (A*, o sin conocer Anchura/Prof)
TODO Llevar todo a un Google Colab para el alumnado
'''
import ctypes
from datetime import datetime
import time
from string import ascii_lowercase
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import matplotlib.transforms
import numpy as np
from matplotlib import image as mpimg
from matplotlib.image import NonUniformImage
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from v002.Agent import Agent, create_agent
from v002.Enviroment import Orientation, OrientationException, Enviroment, TooMuchMovesPerTurn
import v002.Enviroment
from scipy import ndimage
import threading

# class thread_with_exception(threading.Thread):
#     def __init__(self, f, maxTime, intervalTime, parent_thread_id):
#         threading.Thread.__init__(self)
#         self.f = f
#         self.maxTime = maxTime
#         self.intervalTime = intervalTime
#         self.parent_thread_id = parent_thread_id
#
#     def run(self):
#         try:
#             self.f()
#         except Exception as e:
#             print( str(e))
#             pass
#
#     def get_id(self):
#
#         # returns id of the respective thread
#         if hasattr(self, '_thread_id'):
#             return self._thread_id
#         for id, thread in threading._active.items():
#             if thread is self:
#                 return id
#
#     def raise_exception(self):
#         thread_id = self.get_id()
#         res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id),
#                                                          ctypes.py_object(SystemExit))
#         if res > 1:
#             ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
#             print('Exception raise failure')

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

def sleeper(maxTime, intervalTime, notify_thread_id):

    try:
        now = datetime.now()
        init_time = now

        while (now - init_time).seconds < maxTime:
            time.sleep(intervalTime)
            now = datetime.now()

        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(notify_thread_id),
                                                         ctypes.py_object(SystemExit))
    except:
        # print("TIMER has been killed")
        pass

def protect_inf_loop(f, maxTime, intervalTime):
    my_id = threading.current_thread().ident
    t1 = threading.Thread(target=sleeper, args=(maxTime, intervalTime, my_id))
    t1.start()
    try:
        f()
        t1.join(intervalTime)
        if t1.is_alive():
            # t1.raise_exception()
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(t1.ident),
                                                       ctypes.py_object(SystemExit))
            t1.join()

        time.sleep(2 * intervalTime)
    except:
        # print('PARENT HAS BEEN KILLED')
        pass



class Enviroment_with_agents(Enviroment):

    class _Object(ABC):
        def __init__(self, pos_x, pos_y, environment):
            self._pos_x = pos_x
            self._pos_y = pos_y
            self._environment = environment

        @abstractmethod
        def _get_info(self):
            pass

        @abstractmethod
        def plot(self):
            pass

        def _notify_time_iteration(self):
            pass

    class __Food(_Object):
        def __init__(self, pos_x, pos_y, period, environment):
            super().__init__(pos_x, pos_y, environment)
            self._period = period
            self._time_since_eaten = period + 1
            self.__nutrients = period - 1
            self.__my_avatar = pl.imread("images/PixelTomato.bmp")
            self.__my_avatar_2 = pl.imread("images/PixelNoTomato.bmp")

        def is_active(self):
            if self._time_since_eaten > self._period:
                return True

        def plot(self):
            if self.is_active():
                # pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'go', markersize=3)
                pl.gca().imshow(self.__my_avatar,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])
            else:
                pl.gca().imshow(self.__my_avatar_2,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])

        # TODO modificar para que eat vaya disminuyendo una unidad y consuma movimientos, no vida
        # TODO cómo hacer para que una función de aquí se proteja con métodos de HiddenAgent
        def _eat(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            position = hiden_agent._get_position()
            num_moves = hiden_agent._get_num_moves()
            if self.is_active() and position[1] == self._pos_x and \
                    position[0] == self._pos_y and num_moves < self._environment._max_moves_per_turn:
                self._time_since_eaten = 0
                hiden_agent._increase_life(self.__nutrients)
                hiden_agent._send_message({'type': 'life_bonus', 'amount': self.__nutrients,
                                           'Description': 'You have been given ' + str(self.__nutrients) + ' life points, because you have eaten food'})

        def _notify_time_iteration(self):
            if not self.is_active():
                self._time_since_eaten += 1

        def _get_info(self):
            if self.is_active():
                return {'type': 'food type 1', 'Description': 'This is a piece of food from a fixed source of food.'
                                                              ' You eat the food and 1) you get life points, and '
                                                              '2) there will not be food for a number of epochs. '
                                                              'To eat it, you have to '
                                                              'invoke the function in the field eat_function with yourself as argument:'
                                                              '<this_dictionary>[\'eat_function\'](self). You\'d be sent a message '
                                                              'about the life_bonus in '
                                                              'case you do it right. You would not, otherwise',
                        'eat_function': self._eat}
            else:
                return None

    class __Hidden_Agent:
        def __init__(self, name, laberinth, pos_x, pos_y, orientation, life, cmap, color):
            self.__position = [pos_x, pos_y]
            self.__orientation = orientation
            self.__path = [tuple([self.__position[0]+0.5,self.__position[1]+0.5])]
            self.__laberinth = laberinth
            self.__name = name
            self.__num_moves = 0
            self.__my_avatar = {}
            self.__my_avatar[Orientation.DOWN] = pl.imread("images/face1_borders.bmp")#avatar1.bmp")
            self.__my_avatar[Orientation.UP] = ndimage.rotate(self.__my_avatar[Orientation.DOWN],180)
            self.__my_avatar[Orientation.LEFT] = ndimage.rotate(self.__my_avatar[Orientation.UP],90)
            self.__my_avatar[Orientation.RIGHT] = ndimage.rotate(self.__my_avatar[Orientation.UP],270)
            self._life = life
            self._should_stop = False
            self._messages = []
            self._cmap = cmap
            self._color = color

        def _send_message(self,message):
            self._messages.append(message)

        def _get_position(self):
            return self.__position

        def _get_num_moves(self):
            return self.__num_moves

        def _consuming_move(f):
            def inner(self):
                f(self)
                self._life -= 1
                self._send_message({'type':'consuming move', 'Description': 'You have applied a move which consumes life, for instance moving forward',
                                    'amount': 1})

            return inner

        def _and_plot(f):
            def inner(self):
                f(self)

                # No puedo imprimir si es una hebra diferente
                if self.__laberinth._plot_run == 'always':# and not self.__laberinth._Enviroment_with_agents__move_protection:
                    self.__laberinth.plot(clear=True)
            return inner

        def _protected_move(f):
            def inner(self):
                if self.__num_moves < self.__laberinth._max_moves_per_turn:
                    self.__num_moves += 1
                    f(self)
                    # self._life -= 1
                else:
                    self._send_message({'type':'too much moves', 'Description': 'You have tried to do more moves than allowed per turn'})
                    # print("Too much moves per turn")
                    raise TooMuchMovesPerTurn()

            return inner

        def _is_alive(self):
            return self._life > 0 and not self._should_stop

        def _die_protected(f):
            def inner(self,*args, **kwargs):
                if self._is_alive():
                    return f(self,*args, **kwargs)
            return inner

        def _update_path(self):
            self.__path.append(tuple([self.__position[0] + 0.5, self.__position[1] + 0.5]))

        def plot(self, length_path = -10):
            path_x = [j[1] for j in self.__path]
            path_y = [j[0] for j in self.__path]
            if self._life > 0:
                label = self.__name + ' ' + str(self._life)
            else:
                label = self.__name + ' died'

            if length_path is not None:
                pl.plot(path_x[length_path:], path_y[length_path:], color=self._color)
            else:
                pl.plot(path_x, path_y, color=self._color)
            pl.plot(self.__position[1] + 0.5, self.__position[0] + 0.5, label= label, color=self._color)  # punto verde
            #Avatars from: https://www.publicdomainpictures.net/en/view-image.php?image=70648&picture=avatars

            if self._life > 0:
                pl.gca().imshow(self.__my_avatar[self.__orientation],#[:,:,1],
                                extent=[self.__position[1] + 0.1, self.__position[1] + 0.9,
                                        self.__position[0] + 0.1, self.__position[0] + 0.9], cmap=self._cmap)
            else:
                pl.gca().imshow(self.__my_avatar[self.__orientation][:,:,1],
                                extent=[self.__position[1] + 0.1, self.__position[1] + 0.9,
                                        self.__position[0] + 0.1, self.__position[0] + 0.9],
                                cmap='gray',vmin=0,vmax=255)

        def _wall_front_agent(self):
            x, y, orientation = self.__position[0], self.__position[1], self.__orientation
            if orientation == Orientation.UP:
                return self.__laberinth._top_panel_at(x, y)
            elif orientation == Orientation.DOWN:
                if x <= 0:
                    return True
                else:
                    return self.__laberinth._top_panel_at(x - 1, y)
            elif orientation == Orientation.LEFT:
                if y <= 0:
                    return True
                else:
                    return self.__laberinth._east_panel_at(x, y - 1)
            elif orientation == Orientation.RIGHT:
                return self.__laberinth._east_panel_at(x, y)
            else:
                raise OrientationException(orientation)

        def _wall_back_agent(self):
            x, y, orientation = self.__position[0], self.__position[1], self.__orientation
            if orientation == Orientation.UP:
                if x <= 0:
                    return True
                else:
                    return self.__laberinth._top_panel_at(x - 1, y)
            elif orientation == Orientation.DOWN:
                return self.__laberinth._top_panel_at(x, y)
            elif orientation == Orientation.LEFT:
                return self.__laberinth._east_panel_at(x, y)
            elif orientation == Orientation.RIGHT:
                if y <= 0:
                    return True
                else:
                    return self.__laberinth._east_panel_at(x, y - 1)
            else:
                raise OrientationException(orientation)

        def _wall_right_agent(self):
            x, y, orientation = self.__position[0], self.__position[1], self.__orientation
            if orientation == Orientation.UP:
                return self.__laberinth._east_panel_at(x, y)
            elif orientation == Orientation.DOWN:
                if y <= 0:
                    return True
                else:
                    return self.__laberinth._east_panel_at(x, y - 1)
            elif orientation == Orientation.LEFT:
                return self.__laberinth._top_panel_at(x, y)
            elif orientation == Orientation.RIGHT:
                if x <= 0:
                    return True
                else:
                    return self.__laberinth._top_panel_at(x - 1, y)
            else:
                raise OrientationException(orientation)

        def _wall_left_agent(self):
            x, y, orientation = self.__position[0], self.__position[1], self.__orientation
            if orientation == Orientation.UP:
                if y <= 0:
                    return True
                else:
                    return self.__laberinth._east_panel_at(x, y - 1)
            elif orientation == Orientation.DOWN:
                return self.__laberinth._east_panel_at(x, y)
            elif orientation == Orientation.LEFT:
                if x <= 0:
                    return True
                else:
                    return self.__laberinth._top_panel_at(x - 1, y)
            elif orientation == Orientation.RIGHT:
                return self.__laberinth._top_panel_at(x, y)
            else:
                raise OrientationException(orientation)

        @_die_protected
        @_and_plot
        def _turn_right_agent(self):
            self.__orientation = self.__orientation.turn_right()

        @_die_protected
        @_and_plot
        def _turn_left_agent(self):
            self.__orientation = self.__orientation.turn_left()

        def _reset_moves(self):
            self.__num_moves = 0

        @_die_protected
        @_protected_move
        @_consuming_move
        @_and_plot
        def _move_forward_agent(self):

            x, y, orientation = self.__position[0], self.__position[1], self.__orientation

            if not self._wall_front_agent():
                if orientation == Orientation.UP:
                    self.__position[0] += 1
                elif orientation == Orientation.DOWN:
                    self.__position[0] -= 1
                elif orientation == Orientation.LEFT:
                    self.__position[1] -= 1
                elif orientation == Orientation.RIGHT:
                    self.__position[1] += 1
                else:
                    raise OrientationException(orientation)

                self.__path.append(tuple([self.__position[0]+0.5,self.__position[1]+0.5]))
            else:
                self._send_message({'type': 'hit the wall',
                                    'Description': 'You have tried to move forward, but there is a wall.'})

        def _whats_here(self):
            x, y = self.__position[1], self.__position[0]
            laberinth = self.__laberinth
            objects = laberinth._whats_here(x, y)
            walls = {'front': self._wall_front_agent(), 'back': self._wall_back_agent(),
                     'left': self._wall_left_agent(), 'right': self._wall_right_agent()}
            return {'walls': walls, 'objects': objects}

        @_die_protected
        def _increase_life(self, value):
            self._life += value

        @_die_protected
        def _decrease_life(self, value):
            self._life -= value
            self._send_message({'type': 'passing time', 'Description': 'Time passes by and you loss life', 'amount': 1})

        def _read_messages(self):
            messages = self._messages.copy()
            self._messages.clear()
            return messages


    def __init__(self, size, max_moves_per_turn = 7,
                 no_adjacents_in_cluster = False,
                 show_construction = False,
                 # entry_at_border = True,
                 # treasure_at_border = True,
                 food_ratio = 0.05,
                 food_period = 10,
                 move_protection = True,
                 plot_run = 'every epoch'):
        super().__init__(size, no_adjacents_in_cluster, show_construction)
            # , entry_at_border,
            #      treasure_at_border)
        self.__hidden_agents = {}
        self.__outer_agents = {}
        self.__outer_agent_ids = {}
        self._max_moves_per_turn = max_moves_per_turn
        self.__objects = {}
        self.__objects_pointers = set()
        self.__living_agent_ids = set()
        self.__move_protection = move_protection
        self._winner = None
        self.__posible_cmaps = [
            'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
        self.__possible_colors = ['tab:blue', 'tab:orange',
                                 'tab:green',
                                 'tab:red','tab:purple',
                                 'tab:brown','tab:pink',
                                 'tab:gray','tab:olive',
                                 'tab:cyan']
        self._plot_run = plot_run

        for i in range(self._size[0]):
            self.__objects[i] = {}
            for j in range(self._size[1]):
                self.__objects[i][j] = []

                if np.random.rand() < food_ratio:
                    new_object = self.__Food(i, j, food_period, self)
                    self.__objects_pointers.add(new_object)
                    self.__objects[i][j].append(new_object)

    def addObject(self, object, pos_x, pos_y):
        self.__objects_pointers.add(object)
        self.__objects[pos_x][pos_y].append(object)

    '''
    En esta función, he introducido el parámetro who_ask para intentar evitar que algún agente intente
    localizar su representación interna en el laberinto
    '''
    def __get_hidden_agent(self, agent, who_ask):
        if isinstance(who_ask, self._Object) and who_ask in self.__objects_pointers:
            id = self.__outer_agent_ids[agent]
            return self.__hidden_agents[id]

    def _whats_here(self, x, y):
        objects = []

        for i in self.__objects[x][y]:
            info = i._get_info()
            if info is not None:
                objects.append(info)

        return objects

    def __random_name(self):
        new_name = ''.join(np.random.choice(list(ascii_lowercase), size=10))

        while new_name in self.__hidden_agents:
            new_name = ''.join(np.random.choice(list(ascii_lowercase), size=10))

        return new_name

    def create_agent(self, name, move_method, pos_x = None, pos_y = None,
                     orientation=None, life=None):
        agent_class = create_agent(move_method)
        if issubclass(agent_class, Agent):
            id = self.__random_name()
            if pos_x is None:
                pos_x = np.random.randint(self._size[0])
            if pos_y is None:
                pos_y = np.random.randint(self._size[1])
            if orientation is None:
                orientation = Orientation.UP
            if life is None:
                life = self._size[0] * self._size[1]
            an_agent = self.__Hidden_Agent(name, self, pos_x, pos_y,
                                           orientation=orientation,
                                           life= life, cmap=self.__posible_cmaps[len(self.__hidden_agents)],
                                           color=self.__possible_colors[len(self.__hidden_agents)])
            self.__hidden_agents[id] = an_agent
            new_agent = agent_class(
                an_agent._move_forward_agent,
                an_agent._turn_left_agent,
                an_agent._turn_right_agent,
                an_agent._whats_here,
                an_agent._read_messages)
            self.__outer_agents[id] = new_agent
            self.__outer_agent_ids[new_agent] = id
            self.__living_agent_ids.add(id)

            return new_agent
        else:
            return None

    def plot(self, clear=True, time_interval = 0.01, length_path=-10):
        if clear:
            self._clear_plot()

        super().plot(False)

        for ii in self.__hidden_agents:
            i = self.__hidden_agents[ii]
            i.plot(length_path)

        for ii in self.__objects:
            for jj in self.__objects[ii]:
                for kk in self.__objects[ii][jj]:
                    kk.plot()

        pl.legend(loc='center left', bbox_to_anchor=(1, 0.5));
        pl.gca().autoscale();
        if clear:
            self._show_plot(time_interval=time_interval)

    def stop_condition(self):
        return len(self.__living_agent_ids) <= 1

    def get_winner(self):
        return self._winner

    def run(self, time_interval=0.1):

        self._epoch = 0

        while not self.stop_condition():
            self._epoch += 1
        # for _ in range(1000):
            for i in self.__hidden_agents:
                an_agent = self.__hidden_agents[i]
                an_agent._update_path()

            self._dying_agents = set()
            for i in self.__living_agent_ids:
                an_agent = self.__hidden_agents[i]
                an_agent._reset_moves()
                an_agent._decrease_life(1)

                if not an_agent._is_alive():
                    self._dying_agents.add(i)

            for i in self._dying_agents:
                self.__living_agent_ids.remove(i)

            self._dying_agents = set()

            if self.__move_protection:
                for i in self.__living_agent_ids:
                    an_agent = self.__outer_agents[i]

                    # Movimiento del agente protegido frente a bucles infinitos
                    # debe tardar menos de X segundos. El test que me ha funcionado en move es el siguiente, que lo corta la excepción
                    # def move(self):
                    #     for i in range(50):
                    #         time.sleep(0.1)
                    #     self.move_randomly()

                    ## CANDIDATO A REEMPLAZAR
                    # X = 1 #TODO no puedo pintar tras cada movimiento y tener hebras
                    # t1 = thread_with_exception(an_agent.move)
                    # # time1 = datetime.datetime.now()
                    # t1.start()
                    # t1.join(X)
                    # if t1.is_alive():
                    #     t1.raise_exception()
                    #     t1.join()
                    #     self.__hidden_agents[i]._send_message({'type': 'too slow',
                    #                                            'Description': 'You are expected to make moves before ' +
                    #                                            str(X) + ' seconds'})
                    #
                    # # time2 = datetime.datetime.now()
                    # # print(time2-time1)

                    protect_inf_loop(an_agent.move,1,0.05)
            else:
                for i in self.__living_agent_ids:
                    an_agent = self.__outer_agents[i]
                    try:
                        an_agent.move()
                    except Exception as e:
                        print(e)

            for i in self._dying_agents:
                self.__living_agent_ids.remove(i)

            for ii in self.__objects:
                for jj in self.__objects[ii]:
                    for kk in self.__objects[ii][jj]:
                        kk._notify_time_iteration()

            if self._plot_run == 'every epoch':
                self.plot(clear=True,time_interval=time_interval)

        if not self._plot_run == 'never':
            pl.ioff()
            self._clear_plot()
            self.plot(clear=False,time_interval=time_interval)
            pl.show()

        return self.get_winner()
