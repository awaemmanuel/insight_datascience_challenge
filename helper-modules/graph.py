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
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = []

     '''
        Setter: Adds an edge to a graph
        
        Edge is assumed as a set of iterable; tuple, list or set
    '''       
    
    def add_edge(self, edge):
        edge = set(edge)
        (v1, v2) = tuple(edge)
        if v1 in self.graph_dict:
            self.graph_dict[v1].append(v2)
        else:
            self.graph_dict[v1] = [v2]

            
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
        vertex_degree = len(neighbors) + neighbors.count(vertex)
        return vertex_degree
    
    
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
        Helper function: Update graph from a list of vertices tha define a sub-graph.
        
        Queue the vertices and create a edge from a vertex to the next in line using
        queue rotatations.
        
        :type list_of_vertices: List[str]
    '''
    def update_graph(self, list_of_vertices):
        # Internally queue vertices and create vertex and edge to neighbors
        q = deque(list_of_vertices)
        
        for _ in xrange(len(list_of_vertices)):
            self.add_vertex(q[0]) # Add vertex into graph
            self.add_edge((q[0], q[1])) # Create edge between both vertex
            q.rotate(-1) # Rotate queue clockwise, so 1st --> last, 2nd --> 1st, 3rd --> 2nd ...
        
        # Clean up
        q.clear()
    
   
    '''
        Overwritten function: To have a representation of graph when printed.
    '''
    
    def __str__(self):
        result = "vertices: "
        for v in self.graph_dict:
            result += str(v) + " "
        res += "\nedges: "
        for e in self.generate_graph_edges():
            result += str(e) + " "
        return result
