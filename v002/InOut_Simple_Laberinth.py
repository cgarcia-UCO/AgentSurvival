from os import path

from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from v002 import Enviroment_with_agents, pl
import numpy as np

from v002.Enviroment import Orientation


class InOut_Simple_Laberinth(Enviroment_with_agents):

    class _Entry(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)

        def plot(self):
            pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'go')  # punto verde

        def _get_info(self):
            return {'type': 'entry', 'Description': 'This is the entry of the laberinth'}

    class _Exit(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images","exit_image.jpg")) # https://www.rawpixel.com/image/5917811/exit-sign-free-public-domain-cc0-photo

        def _exit(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            position = hiden_agent._get_position()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                self._environment._exit_found = True
                self._environment._winner = hiden_agent
                hiden_agent._should_stop = True
                hiden_agent._send_message({'type': 'success laberinth',
                                           'Description': 'You exited from the laberinth'})

        def plot(self):
            # pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'ro') #punto rojo
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.1, self._pos_x + 0.9,
                                    self._pos_y + 0.1, self._pos_y + 0.9])

        def _get_info(self):
            return {'type': 'exit', 'Description': 'This is the exit of the laberinth. '
                                                   'To finish, invoke the function in the field '
                                                   'exit_function with yourself as argument:'
                                                   '<this_dictionary>[\'exit_function\'](self). You\'d be sent a success message '
                                                   ' in '
                                                   'case you do it right. You would not, otherwise',
                    'exit_function': self._exit}

    class _Treasure(_Exit):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images","chest.png"))

        def plot(self):
            # https://www.rawpixel.com/image/7371573
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8])

    def __init__(self, size, entry_at_border=True, exit_at_border=True, plot_run='every epoch',
                 move_protection = True,remove_walls_prob=0):
        moves_per_turn = 10*size*size
        super().__init__(size, max_moves_per_turn=moves_per_turn,
                         no_adjacents_in_cluster = True,
                         show_construction = False,
                         # entry_at_border = True,
                         # treasure_at_border = True,
                         food_ratio = 0.,
                         food_period = 100000,
                         move_protection = move_protection,
                         plot_run=plot_run,
                         remove_walls_prob=remove_walls_prob)

        self._entry_at_border = entry_at_border
        self._exit_at_border = exit_at_border
        self._start_orientation = Orientation.UP
        self._exit_found = False
        self.times_visited = np.zeros((self._size[0], self._size[1]))

        pos_x = np.random.randint(self._size[0])
        pos_y = np.random.randint(self._size[1])

        if self._entry_at_border:
            axis = np.random.choice([0,1])
            if axis == 0:
                pos_x = np.random.choice([0, self._size[axis] - 1])
                if pos_x == 0:
                    self._start_orientation = Orientation.RIGHT
                else:
                    self._start_orientation = Orientation.LEFT
            else:
                pos_y = np.random.choice([0, self._size[axis] - 1])
                if pos_y == 0:
                    self._start_orientation = Orientation.UP
                else:
                    self._start_orientation = Orientation.DOWN

        self.entry = self._Entry(pos_x, pos_y, self)
        self.addObject(self.entry, pos_x, pos_y)
        pos_x = np.random.randint(self._size[0])
        pos_y = np.random.randint(self._size[0])

        if exit_at_border != 'no exit':
            if self._exit_at_border:
                axis = np.random.choice([0, 1])

                if axis == 0:
                    pos_x = np.random.choice([0, self._size[axis] - 1])
                else:
                    pos_y = np.random.choice([0, self._size[axis] - 1])

                exit = self._Exit(pos_x, pos_y, self)
                self.addObject(exit, pos_x, pos_y)
            else:
                treasure = self._Treasure(pos_x, pos_y, self)
                self.addObject(treasure, pos_x, pos_y)


    def stop_condition(self):
        num_cells_visited = {'null': 0}
        if self._exit_at_border == 'no exit':
            agents = self._Enviroment_with_agents__hidden_agents
            first_agent_path = agents[list(agents.keys())[0]]._Hidden_Agent__path

            for i in range(self._size[0]):
                for j in range(self._size[1]):
                    self.times_visited[i][j] = np.sum([cell[0] == i + 0.5 and cell[1] == j + 0.5
                                           for cell in first_agent_path])

            num_cells_visited = {agents[i]._name:
                                     len(np.unique([str(j[0]) + str(j[1])
                                                    for j in agents[i]._Hidden_Agent__path]))
                                 for i in agents}

            if  self._plot_run == 'every epoch':
                print(num_cells_visited)


        return len(self._Enviroment_with_agents__living_agent_ids) <= 0 or self._exit_found or\
               np.max([num_cells_visited[i] for i in num_cells_visited]) >= self._size[0] * self._size[1]#(self._epoch > 10 * self._size[0] * self._size[1]) or self._exit_found

    def create_agent(self, name, agent_class, life=None):
        if life is None and self._exit_at_border == 'no exit':
            life = 10* self._size[0] * self._size[1]
        elif life is None:
            life = 10* self._size[0] * self._size[1]
        super().create_agent(name, agent_class,
                             self.entry._pos_y,
                             self.entry._pos_x,
                             self._start_orientation,
                             life=life)

    def plot(self, clear=True, time_interval=0.01):

        if self._exit_at_border == 'no exit':
            if clear:
                self._clear_plot()
            super().plot(False, time_interval, None)#clear, time_interval, None)

            if 'hot_alpha' not in plt.colormaps():
                ncolors = 256
                color_array = plt.get_cmap('hot')(range(ncolors))
                color_array[:, -1] = 0.2
                # create a colormap object
                map_object = LinearSegmentedColormap.from_list(name='hot_alpha', colors=color_array)

                # register this new colormap with matplotlib
                plt.register_cmap(cmap=map_object)
            plt.imshow(1- (self.times_visited / np.max(np.max(self.times_visited))), cmap='hot_alpha', interpolation='nearest',
                       extent=[0, self._size[0],
                               self._size[1], 0])
            if clear:
                self._show_plot(time_interval=time_interval)
        else:
            super().plot(clear, time_interval, None)

class No_Walls_Laberinth(InOut_Simple_Laberinth):
    def __init__(self, size, plot_run = 'every epoch', move_protection=True):
        super().__init__(size, entry_at_border=False, exit_at_border=False,
                         plot_run=plot_run,
                         move_protection=move_protection)
        self._h_panels = np.zeros(self._size)
        self._v_panels = np.zeros(self._size)
        self._h_panels[self._size[0]-1,:] = 1
        self._v_panels[:,self._size[1]-1] = 1

    def _initClusters(self):
        return [], None, None
