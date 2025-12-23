# Written by Juan Pablo Gutierrez
# Date: 2025-12-22
# This file contains the function to visualize the graph
# Written by Juan Pablo Gutierrez

import osmnx as ox
import networkx as nx
import folium

place = input("Enter the place: ")

# Download road network for a city
G = ox.graph_from_place(place, network_type="drive")

orig = next(iter(G.nodes))
dest = list(G.nodes)[-1]

route = nx.astar_path(
    G,
    source=orig,
    target=dest,
    
    weight="length"
)

def create_map(G, route):
    # we define the edges for the complete graph (the map) and for the route (the shortest path between origin and destination)
    edges = ox.convert.graph_to_gdfs(G, nodes=False)
    route_edges = ox.routing.route_to_gdf(G, route, weight="length")


    # we create the map and add the edges for the complete graph and the route
    m = edges.explore(tiles="cartodbpositron", color="blue")
    m = route_edges.explore(m=m, color="red", style_kwds={"weight": 5})

    m.save("map.html")

def create_pretty_map(G, route):
    # Get coordinates for the route nodes
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

    # Get center point for the map
    center_lat = sum(coord[0] for coord in route_coords) / len(route_coords)
    center_lon = sum(coord[1] for coord in route_coords) / len(route_coords)

    # Create folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add route as a polyline
    folium.PolyLine(
        route_coords,
        color='red',
        weight=5,
        opacity=0.7
    ).add_to(m)

    # Add markers for origin and destination
    orig_coords = (G.nodes[orig]['y'], G.nodes[orig]['x'])
    dest_coords = (G.nodes[dest]['y'], G.nodes[dest]['x'])

    folium.Marker(
        location=orig_coords,
        popup='Origin',
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)

    folium.Marker(
        location=dest_coords,
        popup='Destination',
        icon=folium.Icon(color='blue', icon='stop')
    ).add_to(m)

    m.save("route.html")

create_map(G, route)
create_pretty_map(G, route)