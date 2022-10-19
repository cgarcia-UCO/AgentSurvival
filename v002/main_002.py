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
import asyncio
import datetime
import sys
import time

from v002 import *
from v002.Agent import create_agent
from v002.Enviroment_with_agents import blocking_printer
from v002.InOut_Simple_Laberinth import InOut_Simple_Laberinth, No_Walls_Laberinth

def read_file(filename):
    code = ''
    copying = False
    with open(filename,'r') as f:
        line = f.readline()
        while line:
            if copying and 'Genotype:' not in line:
                code += line
            elif 'Phenotype:' in line:
                copying = True
            elif 'Genotype:' in line:
                break
            line = f.readline()

        print(code, flush=True)
        return code

def reformat(code):
    result = 'def move(self):\n'
    num_tabs = 1
    lines = code.split('\n')

    for i in lines:
        if i == 'INIT_BLOCK':
            num_tabs += 1
        elif i == 'END_BLOCK':
            num_tabs -= 1
        else:
            for _ in range(num_tabs):
                result += '   '

            result += i.strip() + '\n'

    return result


def do_nothing(self):
    # print("I am nothing", end='')
    pass


def move_randomly(self, message='I am the fast one'):
    # blocking_printer.print(message)#, flush=True)
    messages = self._read_messages_function()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['life_bonus',
                                 'too slow',
                                 'passing time',
                                 'consuming move',
                                 'too much moves',
                                 'too much moves2',
                                 'punched',
                                 'punch success']:
                print(i, flush=True)

    whats_here = self._whats_here_function()
    objects = whats_here['objects']
    walls = whats_here['walls']
    for i in objects:
        if i['type'] not in ['food type 1', 'agent']:
            print(i, flush=True)

        if i['type'] == 'food type 1':
            while i['eat_function'](self) == 1:
                # print("I eat something!!")
                pass

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

def move_randomly_and_punch(self, message='I am the fast one'):
    # blocking_printer.print(message)#, flush=True)
    messages = self._read_messages_function()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['life_bonus',
                                 'too slow',
                                 'passing time',
                                 'consuming move',
                                 'too much moves',
                                 'too much moves2',
                                 'punched',
                                 'punch success']:
                print(i, flush=True)

    whats_here = self._whats_here_function()
    objects = whats_here['objects']
    walls = whats_here['walls']
    for i in objects:
        if i['type'] not in ['food type 1', 'agent']:
            print(i, flush=True)

        if i['type'] == 'food type 1':
            while i['eat_function'](self) == 1:
                # print("I eat something!!")
                pass
        elif i['type'] == 'agent':
            i['punch_function'](self) # TODO controlar que se pasa a sí mismo y no a otro. Quizás comprobar de quién es el turno

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


def exit_from_laberinth_complex(self, message=''):

    # Función que mueve al agente hacia adelante y anota en memoria que ha visitado esa casilla
    # También anota si está pasando por una casilla ya visitada
    # Utiliza un vector dirección
    def move_and_annotate(self):
        self.move_forward()
        self.current_pos[0] = self.current_pos[0] + self.direction[0]
        self.current_pos[1] = self.current_pos[1] + self.direction[1]

        if str(self.current_pos[0]) not in self.visited or \
            str(self.current_pos[1]) not in self.visited[str(self.current_pos[0])] or \
            not self.visited[str(self.current_pos[0])][str(self.current_pos[1])] > 0:\
                self.needed_to_go_back = False
        else:
            self.needed_to_go_back = True

        self.visited[str(self.current_pos[0])] = self.visited.get(str(self.current_pos[0]), {})
        self.visited[str(self.current_pos[0])][str(self.current_pos[1])] = self.visited[str(self.current_pos[0])].get(str(self.current_pos[1]), 0) + 1

    # Creación de estructuras necesarias al inicio para poder recordar las casillas visitadas
    if not hasattr(self, 'visited'):
        self.visited = {'0': {'0': 1}}
        self.direction = [1,0]
        self.current_pos = [0,0]
        self.needed_to_go_back = False
        self.turned_left = False

    # Cálculo de las coordenadas de la casilla delantera y el número de veces que la ha pisado
    front_cell_coords = [str(self.current_pos[0] + self.direction[0]), str(str(self.current_pos[1] + self.direction[1]))]
    if front_cell_coords[0] in self.visited and front_cell_coords[1] in self.visited[front_cell_coords[0]]:
        front_visited = self.visited[front_cell_coords[0]][front_cell_coords[1]]
    else:
        front_visited = 0

    # Cálculo de las coordenadas de la casilla derecha y el número de veces que la ha pisado
    right_cell_coords = [str(self.current_pos[0] - self.direction[1]), str(str(self.current_pos[1] + self.direction[0]))]
    if right_cell_coords[0] in self.visited and right_cell_coords[1] in self.visited[right_cell_coords[0]]:
        right_visited = self.visited[right_cell_coords[0]][right_cell_coords[1]]
    else:
        right_visited = 0

    # Cálculo de las coordenadas de la casilla izquierda y el número de veces que la ha pisado
    left_cell_coords = [str(self.current_pos[0] + self.direction[1]), str(str(self.current_pos[1] - self.direction[0]))]
    if left_cell_coords[0] in self.visited and left_cell_coords[1] in self.visited[left_cell_coords[0]]:
        left_visited = self.visited[left_cell_coords[0]][left_cell_coords[1]]
    else:
        left_visited = 0

    # Leer mensajes e imprimir aquellos que no se conocen
    # print(message, end='')
    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move', 'hit the wall']:  # , 'too much moves']:
                pass
                # print(i)

    # Ver los objetos y salir en caso de estar en la casilla de salida
    whats_here = self.whats_here()
    objects = whats_here['objects']
    walls = whats_here['walls']
    for i in objects:
        if i['type'] == 'exit':
            i['exit_function'](self)

    # Ir a la izquierda si no hay pared y
    # o no se ha visitado, o se ha visitado y es la casilla accesible menos veces visitada
    if walls['right'] == 0 and (right_visited == 0 or (self.needed_to_go_back and
                                                       (right_visited < front_visited or walls['front']) and
                                                       (right_visited < left_visited or walls['left']))):
        self.turn_right()
        #Actualizar el vector de dirección
        if self.direction[0] != 0:
            self.direction[1] = self.direction[0]
            self.direction[0] = 0
        else:
            self.direction[0] = -1 * self.direction[1]
            self.direction[1] = 0
        move_and_annotate(self)
        self.turned_left = False

    # En otro caso, ir de frente si no hay pared y
    # o no se ha visitado o es la casilla accesible menos visitada
    elif walls['front'] == 0 and (front_visited == 0 or (self.needed_to_go_back and
                                                         (front_visited < left_visited or walls['left']))):
        move_and_annotate(self)
        self.turned_left = False

    # En otro caso, girar a la izquierda
    else:
        self.turn_left()
        #Actualizar el vector de dirección
        if self.direction[0] != 0:
            self.direction[1] = -1 * self.direction[0]
            self.direction[0] = 0
        else:
            self.direction[0] = self.direction[1]
            self.direction[1] = 0

        #No estoy seguro de que esto sea necesario. La idea es que si ha girado dos veces a la izquierda, entonces avance
        if self.turned_left:
            move_and_annotate(self)
            self.turned_left = False
        else:
            self.turned_left = True

    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move']:
                pass
                # print(i)

def exit_from_laberinth_complex_v2(self, message=''):

    # Función que mueve al agente hacia adelante y anota en memoria que ha visitado esa casilla
    # También anota si está pasando por una casilla ya visitada
    # Utiliza un vector dirección
    def move_and_annotate(self):
        self.move_forward()
        self.current_pos[0] = self.current_pos[0] + self.direction[0]
        self.current_pos[1] = self.current_pos[1] + self.direction[1]
        current_pos_str = str(self.current_pos[0]) + ',' + str(self.current_pos[1])
        self.visited[current_pos_str] = self.visited.get(current_pos_str, 0) + 1

    # Creación de estructuras necesarias al inicio para poder recordar las casillas visitadas
    if not hasattr(self, 'visited'):
        self.visited = {'0,0': 1}
        self.direction = [1,0]
        self.current_pos = [0,0]

    # Ver los objetos y salir en caso de estar en la casilla de salida
    whats_here = self.whats_here()
    objects = whats_here['objects']
    walls = whats_here['walls']
    for i in objects:
        if i['type'] == 'exit':
            i['exit_function'](self)

    # Ver posibilidades
    posibilities = {'left': not walls['left'], 'right': not walls['right'], 'front': not walls['front']}
    posibilities_times_Visited = {'left': 0, 'right': 0, 'front': 0}

    # Cálculo de las coordenadas de la casilla delantera y el número de veces que la ha pisado
    front_cell_coords = str(self.current_pos[0] + self.direction[0])+','+str(str(self.current_pos[1] + self.direction[1]))
    if front_cell_coords in self.visited:
        posibilities_times_Visited['front'] = self.visited[front_cell_coords]
    else:
        posibilities_times_Visited['front'] = 0

    # Cálculo de las coordenadas de la casilla derecha y el número de veces que la ha pisado
    right_cell_coords = str(self.current_pos[0] - self.direction[1])+','+str(str(self.current_pos[1] + self.direction[0]))
    if right_cell_coords in self.visited:
        posibilities_times_Visited['right'] = self.visited[right_cell_coords]
    else:
        posibilities_times_Visited['right'] = 0

    # Cálculo de las coordenadas de la casilla izquierda y el número de veces que la ha pisado
    left_cell_coords = str(self.current_pos[0] + self.direction[1])+','+str(str(self.current_pos[1] - self.direction[0]))
    if left_cell_coords in self.visited:
        posibilities_times_Visited['left'] = self.visited[left_cell_coords]
    else:
        posibilities_times_Visited['left'] = 0

    # Leer mensajes e imprimir aquellos que no se conocen
    # print(message, end='')
    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move', 'hit the wall']:  # , 'too much moves']:
                # print(i)
                pass

    # Escoger la posibilidad con menos veces visitada. En caso de empate, la prioridad es: derecha, de frente, izquierda
    posibilities_times_Visited = {i:posibilities_times_Visited[i] for i in posibilities if posibilities[i]}
    if len(posibilities_times_Visited) <= 0:
        self.turn_left()
        # Actualizar el vector de dirección
        if self.direction[0] != 0:
            self.direction[1] = -1 * self.direction[0]
            self.direction[0] = 0
        else:
            self.direction[0] = self.direction[1]
            self.direction[1] = 0
    else:
        min_times_visited = np.min([i for i in posibilities_times_Visited.values()])
        posibilities_less_times_visited = [i for i in posibilities_times_Visited if posibilities_times_Visited[i] == min_times_visited]

        # if 'front' in posibilities_less_times_visited:
        #     move_and_annotate(self)
        # elif
        if 'right' in posibilities_less_times_visited:
            self.turn_right()
            #Actualizar el vector de dirección
            if self.direction[0] != 0:
                self.direction[1] = self.direction[0]
                self.direction[0] = 0
            else:
                self.direction[0] = -1 * self.direction[1]
                self.direction[1] = 0
            move_and_annotate(self)

        # En otro caso, ir de frente si no hay pared y
        # o no se ha visitado o es la casilla accesible menos visitada
        elif 'front' in posibilities_less_times_visited:
            move_and_annotate(self)

        # En otro caso, girar a la izquierda
        else:
            self.turn_left()
            #Actualizar el vector de dirección
            if self.direction[0] != 0:
                self.direction[1] = -1 * self.direction[0]
                self.direction[0] = 0
            else:
                self.direction[0] = self.direction[1]
                self.direction[1] = 0

    messages = self.read_messages()
    if len(messages) > 0:

        for i in messages:
            if i['type'] not in ['too slow', 'passing time', 'consuming move']:
                pass
                # print(i)

def exit_from_laberinth(self, message=''):
    print(message, end='')
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

    def slow_move(self):
        move_randomly(self,message='I am the slower')

        # Esto es para testear que el agente implementado tarda mucho en tomar una decisión
        now = datetime.datetime.now()
        init_time = now
        random_time = np.random.random() * 5 + 0.15

        while (now - init_time) < datetime.timedelta(seconds=random_time):
            now = datetime.datetime.now()

        print('He esperado los', random_time, 'segundos', flush=True)

    lb1 = Enviroment_with_agents(15, max_moves_per_turn=7,
                                 plot_run='every epoch',
                                 move_protection=False, remove_walls_prob=0.5)
    # lb1.plot()
    # x = 2
    for i in range(int(x/2)):
        lb1.create_agent('Runner' + str(i+1), move_randomly)#, life=50)
        lb1.create_agent('Puncher' + str(i + 1), move_randomly_and_punch)#, life=50)# move_randomly)#slow_move)

    return lb1.run()

def test_200inOutLaberingth():
    agent_name = 'YO!'

    def move(self):
        for i in range(3):
            self.turn_right()
            self.move_forward()
            self.move_forward()

    from tqdm import tqdm
    num_runs = 200
    num_success =  0

    for _ in tqdm(range(num_runs)):
      lb1 = InOut_Simple_Laberinth(15, plot_run='never',
                                   # move_protection=False,
                                   remove_walls_prob=0.7,
                                   exit_at_border=False, entry_at_border=False)

      # lb1 = InOut_Simple_Laberinth(13, plot_run='never',
      #                              move_protection=True)
      lb1.create_agent(agent_name, exit_from_laberinth_complex_v2)#exit_from_laberinth_complex)#move)
      winner = lb1.run()

      if winner['winner'] == agent_name:
        num_success += 1

    print("\n\nEncontraste la salida en", num_success, "ocasiones de", num_runs)

def test_agent_as_a_function_in_treasure():
    agent_name = 'YO!'

    code = 'def move(self):\n' \
           '    for i in range(3):\n' \
           '            self.turn_right()\n' \
           '            self.move_forward()\n' \
           '            self.move_forward()\n' \

    code2 = 'def move(self):\n' \
            '    messages = self.read_messages()\n' \
            '    if len(messages) > 0:\n' \
            '        for i in messages:\n' \
            '            if i[\'type\'] not in [\'too slow\', \'passing time\', \'consuming move\', \'hit the wall\']:  # , \'too much moves\']:\n' \
            '                print(i)\n' \
            '    whats_here = self.whats_here()\n' \
            '    objects = whats_here[\'objects\']\n' \
            '    walls = whats_here[\'walls\']\n' \
            '    for i in objects:\n' \
            '        if i[\'type\'] == \'exit\':\n' \
            '            i[\'exit_function\'](self)\n' \
            '    if walls[\'right\'] == 0:\n' \
            '        self.turn_right()\n' \
            '        self.move_forward()\n' \
            '    elif walls[\'front\'] == 0:\n' \
            '        self.move_forward()\n' \
            '    else:\n' \
            '        self.turn_left()\n' \
            '    messages = self.read_messages()\n' \
            '    if len(messages) > 0:\n' \
            '        for i in messages:\n' \
            '            if i[\'type\'] not in [\'too slow\', \'passing time\', \'consuming move\']:\n' \
            '                print(i)\n'

    code_inout = 'def move(self):\n' \
            '    whats_here = self.whats_here()\n' \
            '    objects = whats_here[\'objects\']\n' \
            '    walls = whats_here[\'walls\']\n' \
            '    for i in objects:\n' \
            '        if i[\'type\'] == \'exit\':\n' \
            '            i[\'exit_function\'](self)\n' \
            '    if walls[\'right\'] == 0:\n' \
            '        self.turn_right()\n' \
            '        self.move_forward()\n' \
            '    elif walls[\'front\'] == 0:\n' \
            '        self.move_forward()\n' \
            '    else:\n' \
            '        self.turn_left()\n' \

    code_inout = 'def move(self):\n' \
            '   whats_here = self.whats_here()\n' \
            '   walls = whats_here[\'walls\']\n' \
            '   objects = whats_here[\'objects\']\n' \
            '' \
            '   for i in objects:\n' \
            '       if i[\'type\'] == \'exit\':\n' \
            '           i[\'exit_function\'](self)\n' \
            '' \
            '   self.move_forward()\n' \
            '   self.turn_left()\n' \
            '' \
            '   if walls[\'front\']:\n' \
            '       for i in objects:\n' \
            '            if i[\'type\'] == \'exit\':\n' \
            '                i[\'exit_function\'](self)\n' \
            '' \
            '       self.turn_left()\n' \
            '       self.turn_left()\n'

    code2 = read_file('code.code')

    code2 = reformat(code2)
    # exec(code_inout, globals())
    exec(code2, globals())

    from tqdm import tqdm
    num_runs = 100
    num_success =  0

    for _ in tqdm(range(num_runs)):
      # lb1 = InOut_Simple_Laberinth(15, plot_run='every epoch',
      #                              move_protection=True,
      #                              remove_walls_prob=0.5,
      #                              exit_at_border='no exit',#Nuevo
      #                              entry_at_border=False)
      # lb1 = InOut_Simple_Laberinth(7, plot_run='every epoch',
      #                              move_protection=True,
      #                              remove_walls_prob=0.1,
      #                              exit_at_border=True,
      #                              entry_at_border=True)
      lb1 = InOut_Simple_Laberinth(8, plot_run='every epoch',
                                   move_protection=True,
                                   remove_walls_prob=0.4,
                                   exit_at_border=False,
                                   entry_at_border=False)
      lb1.create_agent(agent_name, move)
      winner = lb1.run()

      if winner['winner'] == agent_name:
        num_success += 1

    print("\n\nEncontraste la salida en", num_success, "ocasiones de", num_runs)


def test_agent_as_a_function_in_laberinth():
    agent_name = 'YO!'

    code = 'def move(self):\n' \
           '    for i in range(3):\n' \
           '            self.turn_right()\n' \
           '            self.move_forward()\n' \
           '            self.move_forward()\n' \

    code2 = 'def move(self):\n' \
            '    messages = self.read_messages()\n' \
            '    if len(messages) > 0:\n' \
            '        for i in messages:\n' \
            '            if i[\'type\'] not in [\'too slow\', \'passing time\', \'consuming move\', \'hit the wall\']:  # , \'too much moves\']:\n' \
            '                print(i)\n' \
            '    whats_here = self.whats_here()\n' \
            '    objects = whats_here[\'objects\']\n' \
            '    walls = whats_here[\'walls\']\n' \
            '    for i in objects:\n' \
            '        if i[\'type\'] == \'exit\':\n' \
            '            i[\'exit_function\'](self)\n' \
            '    if walls[\'right\'] == 0:\n' \
            '        self.turn_right()\n' \
            '        self.move_forward()\n' \
            '    elif walls[\'front\'] == 0:\n' \
            '        self.move_forward()\n' \
            '    else:\n' \
            '        self.turn_left()\n' \
            '    messages = self.read_messages()\n' \
            '    if len(messages) > 0:\n' \
            '        for i in messages:\n' \
            '            if i[\'type\'] not in [\'too slow\', \'passing time\', \'consuming move\']:\n' \
            '                print(i)\n'

    code_inout = 'def move(self):\n' \
            '    whats_here = self.whats_here()\n' \
            '    objects = whats_here[\'objects\']\n' \
            '    walls = whats_here[\'walls\']\n' \
            '    for i in objects:\n' \
            '        if i[\'type\'] == \'exit\':\n' \
            '            i[\'exit_function\'](self)\n' \
            '    if walls[\'right\'] == 0:\n' \
            '        self.turn_right()\n' \
            '        self.move_forward()\n' \
            '    elif walls[\'front\'] == 0:\n' \
            '        self.move_forward()\n' \
            '    else:\n' \
            '        self.turn_left()\n' \

    code_inout = 'def move(self):\n' \
            '   whats_here = self.whats_here()\n' \
            '   walls = whats_here[\'walls\']\n' \
            '   objects = whats_here[\'objects\']\n' \
            '' \
            '   for i in objects:\n' \
            '       if i[\'type\'] == \'exit\':\n' \
            '           i[\'exit_function\'](self)\n' \
            '' \
            '   self.move_forward()\n' \
            '   self.turn_left()\n' \
            '' \
            '   if walls[\'front\']:\n' \
            '       for i in objects:\n' \
            '            if i[\'type\'] == \'exit\':\n' \
            '                i[\'exit_function\'](self)\n' \
            '' \
            '       self.turn_left()\n' \
            '       self.turn_left()\n'

    # code2 = read_file('code.code')
    # code2 = reformat(code2)

    # exec(code_inout, globals())
    exec(code_inout, globals())

    from tqdm import tqdm
    num_runs = 100
    num_success =  0

    for _ in tqdm(range(num_runs)):
      # lb1 = InOut_Simple_Laberinth(15, plot_run='every epoch',
      #                              move_protection=True,
      #                              remove_walls_prob=0.5,
      #                              exit_at_border='no exit',#Nuevo
      #                              entry_at_border=False)
      lb1 = InOut_Simple_Laberinth(7, plot_run='every epoch',
                                   move_protection=True,
                                   remove_walls_prob=np.random.rand()/10.,#0.1,
                                   exit_at_border=True,
                                   entry_at_border=True)
      lb1.create_agent(agent_name, move)
      winner = lb1.run()

      if winner['winner'] == agent_name:
        num_success += 1

    print("\n\nEncontraste la salida en", num_success, "ocasiones de", num_runs)


def test_inOutLaberinth():
    lb1 = InOut_Simple_Laberinth(15, plot_run='every epoch', exit_at_border=True)

    x = 1
    # lb1.create_agent('do nothing', do_nothing)

    for i in range(x):
        # lb1.create_agent('silly' + str(i+1), move_silly)
        # lb1.create_agent('Random' + str(i + 1), move_randomly)
        lb1.create_agent('Smarter', exit_from_laberinth_complex_v2)#exit_from_laberinth_complex) #exit_from_laberinth)
        # lb1.create_agent('RightWall', exit_from_laberinth)
    winner = lb1.run()

    if winner is not None:
        print("There was a winner: ", winner)




def test_inOutLaberinth_complex():
    lb1 = InOut_Simple_Laberinth(15, plot_run='every epoch',#'end',#'every epoch',
                                 # move_protection = False,
                                 remove_walls_prob=0.5,
                                 exit_at_border=False,#'no exit',
                                 entry_at_border=False)

    x = 1

    for i in range(x):
        lb1.create_agent('Simpler', exit_from_laberinth_complex_v2)#exit_from_laberinth_complex) #exit_from_laberinth)
        # lb1.create_agent('Good', exit_from_laberinth_complex) #exit_from_laberinth)
    winner = lb1.run()

    if winner is not None:
        print("There was a winner: ", winner)

def test_emptyLaberinth():
    lb1 = No_Walls_Laberinth(10, plot_run='always')

    lb1.create_agent('yo', exit_from_laberinth)
    winner = lb1.run()

    if winner is not None:
        print("There was a winner")

if __name__ == '__main__':
        #np.random.seed(123456)

        #test_xAgents(8)
        # test_2000Laberithns()
        # num_wins = {}
        # for _ in range(20):
        #     winners = test_xAgents(10)
        #
        #     for i in winners:
        #         num_wins[i] = num_wins.get(i,0) + 1
        #
        # print(num_wins)

        # np.random.seed(3)
        state = ('MT19937', np.array([2147483648,  646253997, 3631584960, 3271875430, 2414265262,
                                   2391953290, 2947120412,  500026015,  878763896, 2713300849,
                                   2620673857, 1500392300,  792266513, 2224742946, 4215664432,
                                   3732067456, 3586035270, 3171914599,  996916702, 3953832968,
                                   1471982644, 3904637156, 3371365703, 2167768999,  933522172,
                                   3502496459, 1858925241, 4056145025, 4102603488, 2226433100,
                                   173754926, 2992235627, 1613182751, 1092945805,  542695917,
                                   716597332, 2819979741, 4108795519, 4178051261, 2950834736,
                                   2828070920, 1939261918, 4164169793, 2603066277,  377154514,
                                   1240697291, 4255303383, 3588794522, 3836773832, 1197485704,
                                   2083799425, 2962671284,    3090727, 2157906247, 1678517945,
                                   4043613206, 2190798924,  352501898, 2395151798, 1680275428,
                                   1484393362, 3170889863, 3185090221, 2127858278, 3782415819,
                                   183292612, 1340979544, 1848022852, 1480959757, 2770197253,
                                   1150351909, 1582180892, 4201624695,  737587262, 1824413643,
                                   1587306910, 1153310614, 1405898868, 3401763511, 1461578991,
                                   2581118752, 3045142249, 3839317602, 4008911441,  343538417,
                                   2972118142, 3909894329, 2393397562, 2636324219, 1534266491,
                                   3091886143,  106588184, 1459723881, 3456388092, 1442528654,
                                   519884238, 3356471863, 3674116438, 3937666817, 2115539450,
                                   483119107, 1076381616,  440318859, 2134305252, 4246980283,
                                   2042347251, 1671500756, 1956695330,   62921576, 1462405650,
                                   3350570176, 3713394471,  687000714,  236200188,  322385538,
                                   2514679488, 1569735064, 1184088139, 1826177644,   42312855,
                                   3277903544, 2587506866, 2253389114, 1370228078, 2334182856,
                                   1223647639,  358423080, 2397798233, 2885205056,  817130908,
                                   2895597090, 3227903495,  381289714, 1092123136,   51766688,
                                   3788170392, 2980806835,  178528876, 2118506800, 1242237449,
                                   2045892569, 3980545530,  787285656, 3362664604, 2440542351,
                                   834261457, 3248642839, 4157872758, 3919808555, 3165939436,
                                   2797205260, 1070369630,  410729251, 2174231952, 2163126427,
                                   3929117043, 3919924685, 2340710780,  758872398, 2380286418,
                                   424649847,  791304066, 1752808908,  486624739, 2658197944,
                                   282612800,  578760650, 2879985787, 2981558062, 3746564888,
                                   2594326231, 3338256507,  786359670, 3039186718, 3947930661,
                                   4067596544, 2801779079, 3769367363, 3222540705, 4117819730,
                                   1673718986,  544711599, 3589899084,  970668745, 3019221805,
                                   2624058351, 1436283630, 1232906430, 2300563703, 1590620342,
                                   951717839, 3397101769, 2530554989, 2069786998, 2242137873,
                                   153161283, 1990931427, 3799364205, 2688889584, 3026196018,
                                   3808270053, 1028360323, 3079600379, 1857905599, 2758339904,
                                   359563478, 2459076327,  156016830, 3515473265, 1659776902,
                                   398086415,  562592554, 4171695151, 3361289985, 2697158006,
                                   1055898493, 1193781631, 3375511610, 3114280405,  552836273,
                                   3153898644,   20833989, 2260990646, 3700334012, 2233566489,
                                   866883075,  577086416, 2454548399, 1465501073,  829876462,
                                   3398729505, 1294961149, 2622535112, 3555814073,  675048521,
                                   2022833939, 2040293172, 3655644892, 3985087218, 4171485393,
                                   3490660983,  861354943, 1778110542, 1814404359, 2135555393,
                                   2892399806, 3676412308, 2735470361,   63584274, 2885793929,
                                   1774151370, 2652126422,  999296888, 1118882248,  871305370,
                                   4292649070, 2621962751, 3929496863, 1529523615,   21574955,
                                   2805983095, 1515345738, 4061644962, 4019313859, 2517371156,
                                   4123127561, 2891028260,  868957641, 3464540840,  344401471,
                                   1994476180, 1697481695,  437130742, 3432806132, 3312315352,
                                   827673335, 3905816390, 2199584578, 2286726649, 1024941957,
                                   617461141, 1241930766, 1177551429, 2020127018, 1414102561,
                                   2441467261,  217015450, 3974422230, 2962774944,  193059113,
                                   1577990075, 3149718878, 4130190309,  578696422, 4094875047,
                                   3953920638, 4085153766, 2206746048, 2414935941,  274777314,
                                   77198641,  394435514, 1661862011, 1480458572, 2802496114,
                                   1175958527,  530954768,  552317641, 1845489911,  528235172,
                                   1214587600, 2973106212, 2787311867, 1823444263, 2711608042,
                                   2983173645, 3035206401, 1142369391, 1168903897, 2298501554,
                                   3077816267,  428572067, 3332053038, 1201099509, 2823224078,
                                   4152901008, 2955744920, 3760533623, 2554796639, 1047173538,
                                   2128518571, 1610581245,  813891498, 3866700225, 1047680519,
                                   1060219075, 3998954659, 2700838803,  816933380, 1433583056,
                                   927684035, 3355393703, 1458980675, 2293611303, 2262839992,
                                   1277308714, 4045128046, 3841846975, 4160703127, 3285279273,
                                   2933341858, 1813758761,  620235456, 3832136641,  242375623,
                                   4277400849,  106055322, 1224022893, 3666809658, 3848738741,
                                   195388477, 2904129105, 2946430955, 4199264201, 1037422973,
                                   3487917789,  561932811, 3363036673, 1499513112, 2911807334,
                                   3515817018, 3813383273, 3676359464,  859247087,  738884287,
                                   1109147662, 2910520483,  240361691, 3331057150, 4200532637,
                                   2904266739, 2013478267, 2379070136, 3970638105, 3628733426,
                                   3268017121, 3412935128, 3467218123, 3777652578, 1210371900,
                                   3424879254,  235237207,  798812804, 4270115404, 2707287592,
                                   3841538299, 1768278861, 4061961892, 1126552400, 1453490768,
                                   3261136792,   73250869, 1975727990, 1702391002, 1597762227,
                                   3909787474, 3198322455, 2955190454, 3821917333, 4222831547,
                                   2945611751, 2271776810,  827935025, 2854376666, 2159279302,
                                   904107473, 2001471092,  391201785, 1997671079, 3846146525,
                                   271205346, 2445672798, 2410199581,  216597307, 3708299152,
                                   2602203986, 3296608267, 4046148521, 2535532681,  790817050,
                                   2075217092, 1883256626, 1789465041, 2262855944, 2892371411,
                                   3746168683, 4208392670, 1553417039, 1345203867, 1044930906,
                                   873494728, 1575757412, 1541952669, 4113205480, 3709571315,
                                   6912529, 2641543687, 4138453017,  375144676, 3241027334,
                                   516058231,  713624043, 2810486476, 3452379615, 3958788419,
                                   2058323197, 2101466457, 1335332447, 3696388903, 1902499943,
                                   147265007, 1388897136, 3974271127, 2681739818, 4064588476,
                                   2119063334, 3514105793, 3086991709, 3704958045, 4238915568,
                                   1061755644, 4198046635, 2410229233,  448391089,  731475948,
                                   123428633, 2097051542, 1887093634, 1644922494, 2858792791,
                                   4111548713, 4186863654, 3408044695, 3529558914, 3887194489,
                                   320038539, 3137693360,  769199371, 3296369122, 1218731500,
                                   1147119658, 4053520921, 3698478810, 4039670768, 3337656709,
                                   319100791, 2230141589,  474544288, 3430198721, 1719692194,
                                   4151255399, 2811679566,   36595867, 1373626829,   75066273,
                                   1252145706,  238532930,    8404546, 3594149586, 1193414746,
                                   2603028562,  966787602, 1821283638,  600092908, 1857040389,
                                   1690645671,   89886995, 1779811085, 2668690853, 3825298259,
                                   455133240,  576541845,  317059472, 2214472188, 2417811508,
                                   930249162, 3283707852, 1196262847, 3040278222,  148086459,
                                   2913565468, 2202997997, 1703216653, 1648994833, 4028218796,
                                   2716802941, 3569750430, 2953953817, 3492576345,   98853030,
                                   1364905778, 2213450518,  856941414,  350165741, 2850731730,
                                   2012993875,  767769718, 2863845456, 2922321895, 3197504526,
                                   3115418, 1516529590,  278941752, 2255987775,  212161744,
                                   4059136371,  985653015,  427274575, 2567950970, 2818085514,
                                   3230108159, 3854906413, 2222180806,   66891230,  474975559,
                                   676878720, 2602453419, 1288913345, 4162110156, 4069379845,
                                   1139826821,  632614518, 2802072812, 1085633741, 1949353797,
                                   2340759351, 1352789017, 3151297532, 3290186409, 3224891733,
                                   4172169190, 1623721680,  671017291, 1609790369,  982854797,
                                   1061371019,    5425959, 1266302072,  802352378, 2160814963,
                                   2636516691, 3166818099, 3928425695, 4208196027, 2760271411,
                                   4214161292,  560502752, 2614877827,  228275246, 1882521510,
                                   3172136266, 1936313441, 3046534627, 4066137118, 1579216712,
                                   3311839390, 2911065590, 3198825880, 1488796293, 2304850633,
                                   1996655287,  335361055,  801651456,  637454950, 2194158461,
                                   2441535316, 2981114408, 1849966860,  769797527,  562024701,
                                   2859420359,  970390766,  208830215, 1435281406]), 623, 0, 0.0)
        # np.random.set_state(state)
        # print("Seed: ", np.random.get_state())

        # test_inOutLaberinth()
        test_inOutLaberinth_complex()
        # test_200inOutLaberingth()

        # test_agent_as_a_function_in_treasure()
        # test_agent_as_a_function_in_laberinth()

        # test_emptyLaberinth()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
