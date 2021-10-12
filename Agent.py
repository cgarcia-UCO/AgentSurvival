from abc import abstractmethod, ABC
import numpy as np

class Agent(ABC):
    def __init__(self,
                 move_forward_function,
                 turn_left_function,
                 turn_right_function,
                 whats_here_function,
                 read_messages_function):

        self.__move_forward_function = move_forward_function
        self.__turn_right_function = turn_right_function
        self.__turn_left_function = turn_left_function
        self._whats_here_function = whats_here_function
        self._read_messages_function = read_messages_function

    def turn_right(self):
        self.__turn_right_function()

    def turn_left(self):
        self.__turn_left_function()

    def move_forward(self):
        self.__move_forward_function()

    def read_messages(self):
        return self._read_messages_function()

    def whats_here(self):
        return self._whats_here_function()

    @abstractmethod
    def move(self):
        pass


class SimpleAgent(Agent):

    def __init__(self,
                 move_forward_function,
                 turn_left_function,
                 turn_right_function,
                 whats_here_function,
                 read_messages_function):
        super().__init__(
            move_forward_function,
            turn_left_function,
            turn_right_function,
            whats_here_function, read_messages_function)

    def move_randomly(self):
        whats_here = self._whats_here_function()
        objects = whats_here['objects']
        walls = whats_here['walls']
        for i in objects:
            print(i)

        if not walls['right'] and np.random.rand() < 0.5:
            self.turn_right()
            self.move_forward()
        elif not walls['left'] and np.random.rand() < 0.5:
            self.turn_left()
            self.move_forward()
        elif not walls['front']:
            self.move_forward()
        elif np.random.rand() < 0.5:
            self.turn_left()
        else:
            self.turn_right()

    def move(self):
        self.move_randomly()

def create_agent(move_function):
    class AgentCreator(Agent):

        def __init__(self,
                     move_forward_function,
                     turn_left_function,
                     turn_right_function,
                     whats_here_function,
                     read_messages_function):
            super().__init__(
                move_forward_function,
                turn_left_function,
                turn_right_function,
                whats_here_function, read_messages_function)

        def move(self):
            move_function(self)

    return AgentCreator