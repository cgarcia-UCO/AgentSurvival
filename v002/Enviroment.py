import io
from PIL import Image
import numpy as np
from string import ascii_lowercase
from datetime import datetime
from abc import ABC, abstractmethod
import matplotlib.image as mpimg
from matplotlib.image import BboxImage
from matplotlib.offsetbox import OffsetImage
from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
from v002 import pl, i_am_in_interatcive
import time

from enum import IntEnum
class Orientation(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def turn_right(self):
        v = (self.value + 1) % 4
        return Orientation(v)

    def turn_left(self):
        v = (self.value + 3) % 4
        return Orientation(v)

class OrientationException(Exception):
    pass


'''
Clase que crea laberintos. Se pueden especificar si puede haber más de un camino o no y si las entradas y salidas
deben estar en los bordes.

Para la construcción, se mantiene una lista de celdas con sus adyacentes y una lista de clústeres de celdas.
En cada iteración, se selecciona una celda que sea frontera de un cluster (frontera significa que tiene adyacentes,
los cuales deben ser de otro cluster si no se permite más de un camino, o podría ser del mismo cluster si se permite
más de un camino), y se elimina el panel que conduce a una celda adyacente.
'''
class Enviroment:
    class __Cell:
        def __init__(self, i, j, cluster, adjacents=None):
            self.pos = (i, j)
            self.cluster = cluster
            self.adjacents = adjacents

    class __Cluster:
        def __init__(self, index):
            self.cells = []
            self.frontier = []
            self.index = index

    '''
    Al principio, cada celda pertenece a un único cluster
    '''
    def _initClusters(self):

        cluster = 0
        all_clusters = {}
        all_cells = {}
        cells_2_cluster = {}

        for i in range(self._size[0]):
            for j in range(self._size[1]):
                adjacents = []

                if i > 0:
                    adjacents.append((i - 1, j))
                if j > 0:
                    adjacents.append((i, j - 1))
                if i < self._size[0] - 1:
                    adjacents.append((i + 1, j))
                if j < self._size[1] - 1:
                    adjacents.append((i, j + 1))

                new_cell = self.__Cell(i, j, cluster, adjacents.copy())
                new_cluster = self.__Cluster(cluster)
                new_cluster.cells.append((i, j))
                new_cluster.frontier.append((i,j))
                cells_2_cluster[(i, j)] = cluster

                all_clusters[cluster] = new_cluster
                all_cells[(i, j)] = new_cell
                cluster += 1

        return all_clusters, all_cells, cells_2_cluster

    '''
    Esta función selecciona un par de celdas adyacentes, las devuelve junto a sus clústeres asociados
    '''
    def _select_neighbours(self):
        num_clusters = len(self.all_clusters)
        selected_cluster = list(self.all_clusters.keys())[np.random.randint(0, num_clusters)]
        num_cells_in_frontier = len(self.all_clusters[selected_cluster].frontier)
        selected_cell_index = np.random.randint(0, num_cells_in_frontier)
        selected_cell = self.all_clusters[selected_cluster].frontier[selected_cell_index]
        num_neighbours = len(self.all_cells[selected_cell].adjacents)
        selected_neigh_index = np.random.randint(0, num_neighbours)
        selected_neigh_cell = self.all_cells[selected_cell].adjacents[selected_neigh_index]
        selected_neigh_cluster = self.cells_2_clusters[selected_neigh_cell]

        if selected_neigh_cluster < selected_cluster:
            selected_cell, selected_neigh_cell = selected_neigh_cell, selected_cell
            selected_cluster, selected_neigh_cluster = selected_neigh_cluster, selected_cluster

        return selected_cluster, selected_cell, selected_neigh_cell, selected_neigh_cluster

    '''
    Esta es la función importante, que va creando el laberinto poco a poco.
    '''
    def _iterate_clustering(self):
        # Primero selecciona dos celdas adyacentes
        selected_cluster, selected_cell, selected_neigh_cell, selected_neigh_cluster = self._select_neighbours()
        real_selected_cell = self.all_cells[selected_cell]

        # Eliminamos la adjacencia de i hacia j y si i ya no tiene más adjacentes, la quitamos de la frontera de su cluster
        real_selected_cell.adjacents.remove(selected_neigh_cell)

        if (len(real_selected_cell.adjacents) <= 0):
            self.all_clusters[selected_cluster].frontier.remove(selected_cell)

        # Eliminamos la adjacencia de j hacia i.
        # Añadir esta celda a la frontera, si sigue teniendo adyacentes ocurre en el siguiente bucle
        self.all_cells[selected_neigh_cell].adjacents.remove(selected_cell)

        # Para todas las celdas del cluster de la celda a añadir
        for i in self.all_clusters[selected_neigh_cluster].cells:
            real_neigh_cell = self.all_cells[i]
            real_neigh_cell.cluster = selected_cluster

            # Si no queremos múltiples caminos, hay que eliminar todas las ayacencias entre cada par de celdas
            # de ambos clústeres
            if self.no_adjacents_in_cluster:
                for j in self.all_clusters[selected_cluster].cells:
                    if j in real_neigh_cell.adjacents:
                        real_neigh_cell.adjacents.remove(j)
                        self.all_cells[j].adjacents.remove(i)

                        # Si alguna celda del cluster destino pierde sus adyacencias, hay que sacarlo de la frontera
                        if (len(self.all_cells[j].adjacents) <= 0 and j in self.all_clusters[selected_cluster].frontier):
                            self.all_clusters[selected_cluster].frontier.remove(j)

            # Asignar esta celda al cluster destino
            self.cells_2_clusters[i] = selected_cluster

            if i not in self.all_clusters[selected_cluster].cells:
                self.all_clusters[selected_cluster].cells.append(i)

            # Si la celda añadida (del cluster origen) tiene adyacentes, añadirlo a la frontera
            if len(real_neigh_cell.adjacents) > 0 and i not in self.all_clusters[selected_cluster].frontier:
                self.all_clusters[selected_cluster].frontier.append(i)
            # Puede ocurrir que cluster origen y destino sean el mismo (múltiples caminos), entonces
            # hay que comprobar si sigue teniendo adyacentes y eliminar de la frontera en su caso
            elif len(real_neigh_cell.adjacents) == 0 and i in self.all_clusters[selected_cluster].frontier:
                self.all_clusters[selected_cluster].frontier.remove(i)

        # Eliminar el cluster origen, pues se ha unido al destino
        if selected_cluster != selected_neigh_cluster:
            del self.all_clusters[selected_neigh_cluster]

        # Calcular qué panel hay que quitar
        changing_cell = np.asarray([selected_cell,selected_neigh_cell]).min(axis=0)

        if selected_cell[0] == selected_neigh_cell[0]: #v_panel
            self.__v_panels[changing_cell[0], changing_cell[1]] = 0
        else: #h_panel
            self.__h_panels[changing_cell[0], changing_cell[1]] = 0

    def __init__(self, size, no_adjacents_in_cluster = False, show_construction = False, entry_at_border = True,
                 treasure_at_border = True):
        self._size = (size, size)
        self.__h_panels = []
        self.__v_panels = []
        self.no_adjacents_in_cluster = no_adjacents_in_cluster
        self.show_construction = show_construction
        self.entry_at_border = entry_at_border
        self.treasure_at_border = treasure_at_border
        self.previous_lab_image = None

        self.start_cell = [np.random.randint(self._size[0]), np.random.randint(self._size[1])]
        self.treasure = [np.random.randint(self._size[0]), np.random.randint(self._size[1])]

        if self.entry_at_border:
            axis = np.random.choice([0,1])
            self.start_cell[axis] = np.random.choice([0, self._size[axis] - 1])

        if self.treasure_at_border:
            axis = np.random.choice([0, 1])
            self.treasure[axis] = np.random.choice([0, self._size[axis] - 1])

        self.start_cell = tuple(self.start_cell)
        self.treasure = tuple(self.treasure)

        self.__h_panels = np.ones(self._size)
        self.__v_panels = np.ones(self._size)

        self.all_clusters, self.all_cells, self.cells_2_clusters = self._initClusters()

        if self.show_construction:
            self.plot()
            if i_am_in_interatcive:
                display.display(pl.gcf())
            else:
                pl.ion()
                pl.show()

        # Creación mediante eliminación de paneles hasta que inicio y fin pertenezcan al mismo cluster, o haya más de un cluster

        while len(self.all_clusters) > 1: #self.cells_2_clusters[self.start_cell] != self.cells_2_clusters[self.treasure]:
            if len(self.all_clusters) > 1:
                self._iterate_clustering()

                if self.show_construction:
                    self.plot()

    def _show_plot(self, time_interval = 0.01):
        if i_am_in_interatcive:
            display.display(pl.gcf())
            time.sleep(time_interval)
        else:
            pl.ion()
            pl.pause(time_interval)
            pl.show()

    def _clear_plot(self):
        if i_am_in_interatcive:
            display.display(pl.gcf())
            display.clear_output(wait=True)
        else:
            if pl.isinteractive():
                pl.ion()
            else:
                pl.ioff()
        pl.clf()

    def plot(self, clear=True):

        # ts1 = datetime.now()
        if clear:
            self._clear_plot()

        # ts2 = datetime.now()
        if self.previous_lab_image == None:
            pl.axis('off')
            ax = pl.gca()
            ax.margins(0)
            box_x = [0, self._size[0], self._size[0], 0, 0]
            box_y = [0, 0, self._size[1], self._size[1], 0]
            pl.plot(box_x, box_y)

            for i_1,i in zip(range(self._size[0]), range(1, self._size[0] + 1)):
                for j_1,j in zip(range(self._size[1]), range(1, self._size[1] + 1)):
                    if self.__h_panels[i_1, j_1] == 1:
                        pl.plot([j,j-1],[i,i], color='blue')
                    if self.__v_panels[i_1, j_1] == 1:
                        pl.plot([j,j],[i-1,i],color='blue')

            pl.plot(self.start_cell[1] + 0.5, self.start_cell[0] + 0.5, 'go') #punto verde
            pl.plot(self.treasure[1] + 0.5, self.treasure[0] + 0.5, 'ro') #punto rojo
            buf = io.BytesIO()
            pl.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            self.previous_lab_image = buf
        else:
            ax = pl.gca()
            im = Image.open(self.previous_lab_image)
            ax.imshow(im, extent=[0, self._size[1], 0, self._size[0]])

        # ts3 = datetime.now()
        if clear:
            self._show_plot()

        # ts4 = datetime.now()

        # print('clear: ', ts2 - ts1, ' | plotting: ', ts3 - ts2, ' | show: ', ts4 - ts3)


    def _top_panel_at(self, x, y):
        return self.__h_panels[x,y]

    def _east_panel_at(self, x, y):
        return self.__v_panels[x,y]
