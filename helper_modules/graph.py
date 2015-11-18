from collections import OrderedDict

'''
    Class implementing the behaviors, attributes and functionalities of a graph needed for a
    hashtag graph
    
    Using OrderedDict to hold order of insertion of hashtags into graph.
'''

# Graph implemented with a dictionary
class Graph(object):

    '''
        initializes a graph object
    '''
    
    def __init__(self, graph_dict = OrderedDict()):
        self.graph_dict = graph_dict

    '''
        Getter: Function that returns all vertices currently  of a graph
        :rtype List(str)
    '''
    def get_vertices(self):
        return list(self.graph_dict.keys())

    '''
        Getter: Returns edges of a graph
        :rtype List(set)
    '''
    
    def get_edges(self):
        return self.generate_graph_edges()

    '''
        Setter: Adds a vertex to a graph
        
        If vertex exists in graph, nothing is added, 
        otherwise adds vertex with an empty list
        to collect it's adjacent neighbors. 
    '''
    
    def add_vertex(self, vertex):
        print "=====> add_vertex() Graph before add_vertex: {}".format(self.graph_dict)
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = []
            print "=====> add_vertex() - Adding  vertex: {} to graph now: {}".format(vertex, self.graph_dict)

    '''
        Setter: Adds an edge to a graph
        
        Edge is assumed as a set of iterable; tuple, list or set
    '''       
    
    def add_edge(self, edge):
        print "=====> add_edge() Graph before add_edge: {}".format(self.graph_dict)
        #edge = set(edge)
        (v1, v2) = tuple(edge)
        print "=====> add_edge() -BEFORE ADDING . Adding {} to {}. graph now: {}".format(v2, v1, self.graph_dict)
        if v1 in self.graph_dict:
            if v2 not in self.graph_dict[v1]:
                self.graph_dict[v1].append(v2)
                print "=====> add_edge() - {} already in graph and {} not in list: {}, graph now: {}".format(v1, v2, self.graph_dict[v1], self.graph_dict)
        else:
            self.graph_dict[v1] = [v2]
            print "=====> add_edge() - {} not in graph. Adding {} to {}. {} list: {}, graph now: {}".format(v1, v2, v1, v1, self.graph_dict[v1], self.graph_dict)

            
    '''
        Function that calculates the degree of a single vertex.
        
        Degree being number of edges leading out of a vertex to 
        adject vertices. In general cases a vertex can have a cycle,
        but for simplicity in this challenge we avoid cycles. But if 
        cycles were allowed, then degree of a vertex would be sum of adjacent
        vertices plus occurence of vertex in it's own adject neighbor list
    '''
    
    def vertex_degree(self, vertex):
        neighbors =  self.graph_dict[vertex]
        #print "==> VERTEX: {}, Neighbors: {}".format(vertex, self.graph_dict[vertex])
        degree = len(neighbors) + neighbors.count(vertex)
        return degree
    
    
    '''
        Calculate Complete Graph Average Degrees
    '''
    def get_graph_average_degrees(self):
        running_total = 0
        #print "Graph: {}".format(self.graph_dict)
        for vertex in self.graph_dict:
            running_total += self.vertex_degree(vertex)
            #print "Vertex: {}, Vertex Degree: {}, Running Total: {}, Num Vertices: {}".format(vertex, self.vertex_degree(vertex), running_total, len(self.graph_dict))
        return running_total / float(len(self.graph_dict))
    
    '''
        Helper Function: Generate the edges of the graph.
        
        Edges are internally represented as set two vertices 
    '''
    
    def generate_graph_edges(self):
        edges = []
        for vertex in self.graph_dict:
            for neighbour in self.graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    
   
    '''
        Overwritten function: To have a representation of graph when printed.
    '''
    
    def __str__(self):
        result = "vertices: "
        for v in self.graph_dict:
            result += str(v) + " "
        result += "\nedges: "
        for e in self.generate_graph_edges():
            result += str(e) + " "
        return result
