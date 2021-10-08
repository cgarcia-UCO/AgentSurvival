# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



'''
Se me ocurre crear un Laberinth con objetos. En cada paso, el agente puede preguntar whats_this, que devuelve
un diccionario con object_type, description, y otros (entre otros habrá algunas fucniones). Algunos objetos se pueden
cargar y llevar encima, otros no. Normalmente los objetos tendrá una número limitado de usos. Para usar un objeto,
habrá que utilizar alguna de las funciones dentro del diccionario que devuelve whats_this. Al utilizar dichas funciones,
habrá que modificar algunas cosas almacenadas en el Laberinto, por lo que dichos objetos tendrán que definirse dentro de 
dicha clase
'''



import time

from v002 import *
from v002.Agent import create_agent
from v002.InOut_Simple_Laberinth import InOut_Simple_Laberinth, No_Walls_Laberinth


def do_nothing(self):
    pass

def exit_from_laberinth(self):
    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move', 'hit the wall']:  # , 'too much moves']:
                print(i)

    whats_here = self.whats_here()
    objects = whats_here['objects']
    walls = whats_here['walls']
    for i in objects:
        if i['type'] == 'exit':
            i['exit_function'](self)

    if walls['right'] == 0:
        self.turn_right()
        self.move_forward()
    elif walls['front'] == 0:
        self.move_forward()
    else:
        self.turn_left()


    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move']:
                print(i)


def move_silly(self):
    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move', 'hit the wall']:  # , 'too much moves']:
                print(i)

    for _ in range(10):
        self.turn_right()
        self.move_forward()
        self.move_forward()


def test_2000Laberithns():
    from tqdm import tqdm
    for _ in tqdm(range(1000)):
        lb1 = Enviroment(20, no_adjacents_in_cluster=False, show_construction = False,
                         entry_at_border=False, treasure_at_border=False)
        # pl.ioff()
        # lb1.plot()
        # pl.show()

    print("Second test stage")

    for _ in tqdm(range(1000)):
        lb1 = Enviroment(20, no_adjacents_in_cluster=True, show_construction = False,
                         entry_at_border=False, treasure_at_border=False)

def test_xAgents(x):



    '''
    Tu agente, en las invocaciones al método move debiera:
    1. leer los mensajes recibidos con self._whats_here_function() (es opcional).
    Recibirás una lista de diccionarios (y los mensajes se eliminarán de tu buzón). Cada diccionario es un mensaje recibido.
    Tendra un campo 'type' y un campo 'Description'. Te recomiendo que al principio los imprimas en la consola y los leas,
    y posteriormente realices acciones dependiendo del tipo de mensaje, si es el caso,
    (he imprimas en consola sólo aquellos con un tipo que aún no conozcas).

    2. también debiera ver lo que hay en la casilla en la que se encuentra con self._whats_here_function() (es opcional).
    Recibirás una lista de diccionarios (y los mensajes se eliminarán de tu buzón). Cada diccionario te informa de lo
    encontrado, por lo que te recomiendo que al principio los imprimas en la consola y leas los mensajes, y posteriormente
    realices acciones dependiendo del tipo de objeto encontrado (he imprimas en consola aquellos con un tipo que aún no conozcas).

    3. Y debiera ejecutar las acciones que considere oportunas con las funciones
    - self.turn_right()
    - self.turn_left()
    - self.move_forward()
    - O alguna otra relacionada con algún objeto que hayas encontrado.
    Ten en cuenta que algunas acciones consumen movimientos por turno, y el número de movimientos por turno está limitado.
    Una vez sobrepasado, el resto de movimientos se descartarán. Recibirás mensajes al respecto en tu buzón.
    '''

    '''
    Hay dos formas de crear agentes. Una es creando una subclase de Agente, en el que tienes que mantener el __init__ como 
    en el siguiente ejemplo, y además debes definir el método move().
    
    Otra es definiendo una función cualquiera, y llamando a la función create_agent, del módulo Agent,
    la cual crea una clase con una función move que llama a la función que tú has definido. Esta segunda es la leche,
    pues no necesita que copies el __init__ (no estoy seguro de si realmente es necesario), ni que definas una clase
    '''

    def move_randomly(self):
        messages = self._read_messages_function()
        if len(messages) > 0:

            for i in messages:
                if i['type'] not in ['too slow', 'passing time', 'consuming move']:
                    print(i)

        whats_here = self._whats_here_function()
        objects = whats_here['objects']
        walls = whats_here['walls']
        for i in objects:
            if i['type'] == 'food type 1':
                i['eat_function'](self)
                # print("I eat something!!")

        options = [i for i in walls if (not walls[i]) and (i != 'back')]

        if len(options) <= 0:
            choice = 'back'
        else:
            choice = np.random.choice(options)

        if choice == 'right':
            self.turn_right()
            self.move_forward()
        elif choice == 'left':
            self.turn_left()
            self.move_forward()
        elif choice == 'front':
            self.move_forward()
        else:
            self.turn_left()
            self.turn_left()
            self.move_forward()

        # Esto es para testear que el agente implementado tarda mucho en tomar una decisión
        # for _ in range(40):
        #     time.sleep(0.1)

    # class MyAgent(Agent):
    #
    #     def __init__(self,
    #                  move_forward_function,
    #                  turn_left_function,
    #                  turn_right_function,
    #                  whats_here_function,
    #                  read_messages_function):
    #         super().__init__(
    #             move_forward_function,
    #             turn_left_function,
    #             turn_right_function,
    #             whats_here_function, read_messages_function)
    #
    #     def move_randomly(self):
    #         messages = self._read_messages_function()
    #         if len(messages) > 0:
    #             print(messages)
    #
    #         whats_here = self._whats_here_function()
    #         objects = whats_here['objects']
    #         walls = whats_here['walls']
    #         for i in objects:
    #             if i['type'] == 'food':
    #                 i['eat_function'](self)
    #                 print("I eat something!!")
    #
    #         if not walls['right'] and np.random.rand() < 0.5:
    #             self.turn_right()
    #             self.move_forward()
    #         elif not walls['left'] and np.random.rand() < 0.5:
    #             self.turn_left()
    #             self.move_forward()
    #         elif not walls['front']:
    #             self.move_forward()
    #         elif np.random.rand() < 0.5:
    #             self.turn_left()
    #         else:
    #             self.turn_right()
    #
    #     def move(self):
    #         self.move_randomly()




    lb1 = Enviroment_with_agents(20, max_moves_per_turn=10, no_adjacents_in_cluster=False, show_construction=False,
                                 move_protection=False)
    # lb1.plot()

    for i in range(x):
        lb1.create_agent('yo' + str(i+1), move_randomly)

    lb1.run(0.1)

def test_inOutLaberinth():
    lb1 = InOut_Simple_Laberinth(10)

    x = 1
    lb1.create_agent('do nothing', do_nothing)

    for i in range(x):
        # lb1.create_agent('silly' + str(i+1), move_silly)
        lb1.create_agent('yo' + str(i + 1), exit_from_laberinth)
    lb1.run(0.1)

def test_emptyLaberint():
    lb1 = No_Walls_Laberinth(10)

    lb1.create_agent('yo', exit_from_laberinth)
    lb1.run(0.1)

if __name__ == '__main__':
        #np.random.seed(123456)

        # test_2000Laberithns()
        # test_xAgents(10)


        # test_inOutLaberinth()

        test_emptyLaberint()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
