import networkx as nx
import igraph as ig
import plotly
import plotly.graph_objects as go
import ipywidgets as widgets
import textwrap
from IPython.display import clear_output

# load Graph
G = nx.read_graphml('../data/graph/civ.graphml')

def colornode(by):
    if by == 'Era':
        ERAS = ['Ancient Era','Classical Era', 'Medieval Era', 'Renaissance Era', 'Industrial Era', 'Modern Era', 'Atomic Era', 'Information Era', 'None']
        index = dict(zip(ERAS, plotly.colors.qualitative.G10))
    elif by == 'Type':
        TYPES = ['Building', 'Civic', 'Civilization', 'District', 'Government', 'Improvement', 'Policy', 'Project', 'Resource', 'Technology', 'Unit', 'Wonder', 'Atomic Weapon', 'Leader(s)', 'Diplomacy', 'Casus Belli', 'City-state', 'None']
        index = dict(zip(TYPES, plotly.colors.qualitative.Dark24))
    color_func = lambda G: [index[v] for _, v in sorted(G.nodes.data(by, default='None'))]
    return color_func

def coloredge():
    TYPES = ['Unlocks', 'Boosts', 'Replaces', 'Obsoletes', 'Reveals', 'Harvests', 'Upgrades', 'Builds'] 
    index = dict(zip(TYPES, ['#808080'] + plotly.colors.qualitative.D3))
    return index

def build_plotly(G, coords, colornodeby):
    # nodes, edges
    nX, nY = zip(*[n[1] for n in sorted(coords.items(), key=lambda n: n[0])])
    eX, eY = [[(coords[u][i], coords[v][i]) for u, v in G.edges()] for i in range(2)]
    
    # arrow edges
    edge_colors = [coloredge()[edge] for edge in nx.get_edge_attributes(G, 'Type').values()]
    arrows = dict(showarrow=True, arrowhead=3, arrowsize=1.5, axref='x', ayref='y', standoff=10, startstandoff=10)
    annotations = [dict(x=x[0], y=y[0], ax=x[1], ay=y[1], arrowcolor=color, **arrows) for x, y, color in zip(eX, eY, edge_colors)]
    
    # tooltips
    wrap = lambda i: '<br>'.join(textwrap.wrap(str(i)))
    lines = lambda attrs: '<br>'.join(['<b>{}:</b> {}'.format(k, wrap(v)) for k, v in attrs.items()])
    tips = [lines(attrs) for _, attrs in sorted(G.nodes.data(default='None'))]

    # layout
    marker = dict(size=10, line_width=2)
    axes = dict({
        axis : dict(showgrid=False, zeroline=False, showticklabels=False) for axis in ['xaxis', 'yaxis']
    })
    layout = dict(annotations=annotations, **axes, showlegend=True, margin=dict(t=30, l=10, b=10, r=10), plot_bgcolor='white', height=800, legend_title_text='<b>Edge Types</b>')
    
    nodes = go.Scatter(x=nX, y=nY, mode='markers+text', hoverinfo='text', marker=marker, textposition='top center', textfont_size=14, showlegend=False)
    nodes.hovertext = tips
    nodes.text = sorted(G.nodes)
    nodes.marker.color = colornode(by=colornodeby)(G)
    
    traces = [go.Scatter(name=edge, marker_color=color, x=[0], y=[0], marker_size=1, hoverinfo='skip') for edge, color in coloredge().items()]

    fig = go.Figure(data=nodes, layout=go.Layout(layout))
    fig.add_traces(traces) # add edge legend
    
    fig.show()
    
def draw_network(G, node, direction, radius, nodetypes, edgetypes, colornodeby, enablespec):
    if not node:
        message = 'Please select an Entity.'
        print(message)
        return
    
    node = node.split(' - ')[0]
    
    if isinstance(nodetypes, (list, tuple)) and 'All' not in nodetypes:
        nodes = [n for n, v in nx.get_node_attributes(G, 'Type').items() if v in nodetypes]
        
        if node not in nodes:
            message = '{} is not in this network due to your selected Node Types.\nPlease include {} in the Node Types parameter'.format(node, G.nodes.data()[node]['Type'])
            print(message)
            return
        
        G = G.subgraph(nodes)
    
    if not (G.nodes.data()[node].get('Specificity') or enablespec):
        nodes = [n for n in G.nodes() if n not in nx.get_node_attributes(G, 'Specificity').keys()]
        G = G.subgraph(nodes)
    
    # G, node, direction
    both = True if direction == 'Both' else False
    forward = G if direction == 'Forward' else G.reverse()
    ego = nx.ego_graph(G=forward, n=node, radius=radius, undirected=both)
    ego = ego.reverse() if direction == 'Forward' else ego # flip arrow directions for display
    
    if isinstance(edgetypes, (list, tuple)) and 'All' not in edgetypes: 
        edges = [e for e, v in nx.get_edge_attributes(ego, 'Type').items() if v in edgetypes]
        ego = ego.edge_subgraph(edges)
        if len(ego.edges) < 1:
            message = 'There are no edges in this network due to your selected Edge Types.\nPlease include more Edge Types.'
            print(message)
            return
        
    if len(ego.edges) < 1:
        message = 'There are no edges in this network.\nPlease include more Node Types or change Direction.'
        print(message)
        return
    
    LIMIT = 100
    if len(ego.nodes) > LIMIT:
        message = 'There are more than {} nodes in this network, which slows down graph drawing significantly.\nPlease decrease Radius, select fewer Node or Edge Types, or change Direction.'.format(LIMIT)
        print(message)
        return
    
    # igraph layout
    ego_ig = ig.Graph.TupleList(ego.edges(), directed=True)
    coords = dict(zip(ego_ig.vs['name'], ego_ig.layout('kk').coords))
    
    build_plotly(ego, coords, colornodeby)
    
ENTITIES = sorted(['{} - {}'.format(n, v) for n, v in nx.get_node_attributes(G, 'Type').items()])
wg_node = widgets.Combobox(options=ENTITIES,
                           description='Entity',
                           placeholder='Choose an entity',
                           ensure_option=True)

wg_radius = widgets.IntSlider(value=3,
                              min=1,
                              max=15,
                              step=1,
                              description='Radius')

wg_direction = widgets.ToggleButtons(options=['Forward', 'Backward', 'Both'],
                                     description='Direction')

NODETYPES = ['Building', 'Civic', 'Civilization', 'District', 'Government', 'Improvement', 'Policy', 'Project', 'Resource', 'Technology', 'Unit', 'Wonder',
             'Atomic Weapon', 'Leader(s)', 'Diplomacy', 'Casus Belli', 'City-state']
wg_nodetypes = widgets.SelectMultiple(options=sorted(['All'] + NODETYPES),
                                      value=['All'],
                                      ensure_option=True,
                                      description='Node Types')

EDGETYPES = ['Unlocks', 'Boosts', 'Replaces', 'Obsoletes', 'Reveals', 'Harvests', 'Upgrades', 'Builds'] 
wg_edgetypes = widgets.SelectMultiple(options=['All'] + EDGETYPES,
                                      value=['All'],
                                      ensure_option=True,
                                      description='Edge Types')

wg_colornodeby = widgets.ToggleButtons(options=[('Era', 'Era'), ('Node Type', 'Type')],
                                       description='Color By')

wg_enablespec = widgets.Checkbox(value=False, description='Include Entities Unique to Civs')

wg_drawbutton = widgets.Button(description='Draw Network')

output = widgets.Output()

def draw(_):
    with output:
        clear_output()
        draw_network(G, node=wg_node.value, radius=wg_radius.value, direction=wg_direction.value, nodetypes=wg_nodetypes.value,
                     edgetypes=wg_edgetypes.value, colornodeby=wg_colornodeby.value, enablespec=wg_enablespec.value)


wg_drawbutton.on_click(draw)

demo = widgets.VBox([widgets.HBox([wg_node, wg_radius]), wg_direction, widgets.HBox([wg_nodetypes, wg_edgetypes]), wg_colornodeby, wg_enablespec, wg_drawbutton, output])