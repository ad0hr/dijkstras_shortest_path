# imports
import numpy as np


def spath_iteration(network, unvisited):
    """
    performs one iteration of the shortest-path algorithm
    ------------
    Parameters:
        network (Network object):
            An object that belongs to the network class
        unvisited (set):
            The set containing the names of all currently unsolved nodes in the network
    ------------
    Return:
        solved_name (string or None):
            Name of the node that is solved on the iteration and therefore moved from the unvisited set. If no node can
            be solved, return None
    """
    # find the node in unvisited set with the smallest distance to become the solved node for this iteration
    while len(unvisited) != 0:
        # checks to return None if no node can be solved
        try:
            solved_name = min(unvisited, key=lambda node: network.get_node(node).value[0])
        except ValueError:
            return None

        # removal of the solved node from the unvisited set
        unvisited.discard(solved_name)

        # init
        solved_node = network.get_node(solved_name)

        # finding all the outwardly connected nodes from the solved node
        for arc in solved_node.arcs_out:
            # temporarily storing arc weight, current outwardly connected node and the predecessor node
            temp_weight = arc.weight
            temp_predecessor = arc.from_node
            temp_node = arc.to_node

            # calculating the total distance from source node
            dist_sum = temp_weight + temp_predecessor.value[0]

            # change the provisional distance and predecessor node if the new distance is smaller than current value
            # compared_value
            if dist_sum < temp_node.value[0]:
                temp_node.value[0] = dist_sum
                temp_node.value[1] = solved_node.name

        return solved_name


def spath_extract_path(network, destination_name):
    """
    uses the chain of predecessor nodes to generate a list of node names for the shortest path from source
    to destination node
    -------------
    Parameters:
        network (Network object):
            An object that belongs to the network class
        destination_name (string):
            Name of the destination node
    -------------
    Return:
        path (list):
            List of node names for the shorted path, starting the source node name and ending with the destination
            node name
    --------------
    Notes:
        Only valid if a solution was found for the shortest path
    """
    destination_node = network.get_node(destination_name)
    path = []

    # follow a path through each node to find a chain of predecessors, starting with destination node
    current_node = destination_node
    while current_node.value[1] is not None:
        predecessor_name = current_node.value[1]
        predecessor_node = network.get_node(predecessor_name)
        path.append(predecessor_name)
        current_node = predecessor_node

    # reverse the path, so it goes from start to destination
    path.reverse()
    # include the destination node in path
    path.append(destination_name)

    return path


def spath_algorithm(network, source_name, destination_name):
    """
    performs Dijkstra's shortest-path algorithm
    ------------
    Parameters:
        network (Network object):
            An object that belongs to the network class
        source_name (string):
            The name of the source node
        destination_name (string):
            The name of the destination node
    -------------
    Returns:
        distance (float or None):
            The distance of the shortest path if a solution was found, otherwise return None
        path (list or None):
            List of node names for the shortest path, starting with the source node name and ending with the
            destination node name. If no solution was found, return None.
    """
    # initialise the values for all nodes in the network
    unvisited_set = spath_initialise(network, source_name)

    solved_node_name = spath_iteration(network, unvisited_set)

    # perform iterations of the shortest-path algorithm until the entire path is found
    while solved_node_name != destination_name:
        # if it cannot be solved, break out of the while loop
        if solved_node_name is None:
            break
        solved_node_name = spath_iteration(network, unvisited_set)

    # if it cannot be solved, both the distance and path are set to None to be returned
    if solved_node_name is None:
        distance = None
        path = None
    else:
        # returning the values for distance and path assuming a solution was found
        destination_node = network.get_node(destination_name)
        distance = destination_node.value[0]
        path = spath_extract_path(network, destination_name)

    return distance, path


class Node(object):
    """
    Object representing network node.

    Attributes:
    -----------
    name : str, int
        unique identifier for the node.
    value : float, int, bool, str, list, etc...
        information associated with the node.
    arcs_in : list
        Arc objects that end at this node.
    arcs_out : list
        Arc objects that begin at this node.
    """

    def __init__(self, name=None, value=None, arcs_in=None, arcs_out=None):

        self.name = name
        self.value = value
        if arcs_in is None:
            self.arcs_in = []
        if arcs_out is None:
            self.arcs_out = []

    def __repr__(self):
        return f"node:{self.name}"


class Arc(object):
    """
    Object representing network arc.

    Attributes:
    -----------
    weight : int, float
        information associated with the arc.
    to_node : Node
        Node object (defined above) at which arc ends.
    from_node : Node
        Node object at which arc begins.
    """

    def __init__(self, weight=None, from_node=None, to_node=None):
        self.weight = weight
        self.from_node = from_node
        self.to_node = to_node

    def __repr__(self):
        return f"arc:({self.from_node.name})--{self.weight}-->({self.to_node.name})"


class Network(object):
    """
    Basic Implementation of a network of nodes and arcs.

    Attributes
    ----------
    nodes : list
        A list of all Node (defined above) objects in the network.
    arcs : list
        A list of all Arc (defined above) objects in the network.
    """

    def __init__(self, nodes=None, arcs=None):
        if nodes is None:
            self.nodes = []
        if arcs is None:
            self.arcs = []

    def __repr__(self):
        node_names = '\n'.join(node.__repr__() for node in self.nodes)
        arc_info = '\n'.join(arc.__repr__() for arc in self.arcs)
        return f'{node_names}\n{arc_info}'

    def get_node(self, name):
        """
        Return network node with name.

        Parameters:
        -----------
        name : str
            Name of node to return.

        Returns:
        --------
        node : Node, or None
            Node object (as defined above) with corresponding name, or None if not found.
        """
        # loop through list of nodes until node found
        for node in self.nodes:
            if node.name == name:
                return node

        # if node not found, return None
        return None

    def add_node(self, name, value=None):
        """
        Adds a node to the Network.

        Parameters
        ----------
        name : str
            Name of the node to be added.
        value : float, int, str, etc...
            Optional value to set for node.
        """
        # create node and add it to the network
        new_node = Node(name, value)
        self.nodes.append(new_node)

    def add_arc(self, node_from, node_to, weight):
        """
        Adds an arc between two nodes with a desired weight to the Network.

        Parameters
        ----------
        node_from : Node
            Node from which the arc departs.
        node_to : Node
            Node to which the arc arrives.
        weight : float
            Desired arc weight.
        """
        # create the arc and add it to the network
        new_arc = Arc(weight, node_from, node_to)
        self.arcs.append(new_arc)

        # update the connected nodes to include arc information
        node_from.arcs_out.append(new_arc)
        node_to.arcs_in.append(new_arc)

    def read_network(self, filename):
        """
        Reads a file to construct a network of nodes and arcs.

        Parameters
        ----------
        filename : str
            The name of the file (inclusive of extension) from which to read the network data.
        """
        with open(filename, 'r') as file:

            # get first line in file
            line = file.readline()

            # check for end of file, terminate if found
            while line != '':
                items = line.strip().split(',')

                # create source node if it doesn't already exist
                if self.get_node(items[0]) is None:
                    self.add_node(items[0])

                # get starting node for this line
                source_node = self.get_node(items[0])

                for item in items:

                    # initial item ignored as it has no arc
                    if item == source_node.name:
                        continue

                    # separate out to destination node name and arc weight
                    data = item.split(';')
                    destination_node = data[0]
                    arc_weight = data[1]

                    # Create destination node if not already in network, then obtain the node itself
                    if self.get_node(destination_node) is None:
                        self.add_node(destination_node)
                    destination_node = self.get_node(destination_node)

                    # Add arc from source to destination node, with associated weight
                    self.add_arc(source_node, destination_node, float(arc_weight))

                # get next line in file
                line = file.readline()