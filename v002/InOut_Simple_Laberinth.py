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

        def _exit(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            position = hiden_agent._get_position()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                hiden_agent._life = 0
                self._environment._dying_agents.add(self._environment._Enviroment_with_agents__outer_agent_ids[agent])
                hiden_agent._send_message({'type': 'success laberinth',
                                           'Description': 'You exited from the laberinth'})

        def plot(self):
            pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'ro') #punto rojo

        def _get_info(self):
            return {'type': 'exit', 'Description': 'This is the exit of the laberinth. '
                                                   'To finish, invoke the function in the field '
                                                   'exit_function with yourself as argument:'
                                                   '<this_dictionary>[\'exit_function\'](self). You\'d be sent a success message '
                                                   ' in '
                                                   'case you do it right. You would not, otherwise',
                    'exit_function': self._exit}


    def __init__(self, size, entry_at_border=True, exit_at_border=True):
        moves_per_turn = 10*size*size
        super().__init__(size, max_moves_per_turn=moves_per_turn,
                         no_adjacents_in_cluster = False,
                         show_construction = False,
                         # entry_at_border = True,
                         # treasure_at_border = True,
                         food_ratio = 0.,
                         food_period = 100000,
                         move_protection = False)

        self._entry_at_border = entry_at_border
        self._exit_at_border = exit_at_border
        self._start_orientation = Orientation.UP

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

        if self._exit_at_border:
            axis = np.random.choice([0, 1])

            if axis == 0:
                pos_x = np.random.choice([0, self._size[axis] - 1])
            else:
                pos_y = np.random.choice([0, self._size[axis] - 1])

        exit = self._Exit(pos_x, pos_y, self)
        self.addObject(exit, pos_x, pos_y)

    def create_agent(self, name, agent_class):
        life = 10000
        super().create_agent(name, agent_class,
                             self.entry._pos_y,
                             self.entry._pos_x,
                             self._start_orientation,
                             life)

    def plot(self, clear=True, time_interval=0.01):
        super().plot(clear, time_interval, None)