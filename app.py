# Written by Juan Pablo Gutierrez
# Date: 2025-12-22
# Real-time route visualization app using Streamlit

import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# Page config
st.set_page_config(page_title="Route Finder", layout="wide")

# Initialize session state
if 'route_data' not in st.session_state:
    st.session_state.route_data = None
if 'map_obj' not in st.session_state:
    st.session_state.map_obj = None
if 'show_streets' not in st.session_state:
    st.session_state.show_streets = False
if 'map_rendered' not in st.session_state:
    st.session_state.map_rendered = False

st.title("🗺️ Real-Time Route Finder")
st.markdown("Find the shortest path between two points on a map")
# Sidebar for inputs
with st.sidebar:
    st.header("Settings")
    
    # City/Place input
    place = st.text_input(
        "City/Place",
        value="Mexico City, Mexico",
        help="Enter a city name or place"
    )
    
    st.divider()
    
    st.subheader("Origin")
    orig_lat = st.number_input("Origin Latitude", value=25.686, format="%.6f")
    orig_lon = st.number_input("Origin Longitude", value=-100.316, format="%.6f")
    
    st.divider()
    
    st.subheader("Destination")
    dest_lat = st.number_input("Destination Latitude", value=25.680, format="%.6f")
    dest_lon = st.number_input("Destination Longitude", value=-100.300, format="%.6f")
    
    st.divider()
    
    # Algorithm selection
    algorithm = st.selectbox(
        "Pathfinding Algorithm",
        ["A*", "Dijkstra"],
        help="A* is generally faster, Dijkstra is more accurate"
    )
    
    # Calculate button
    calculate = st.button("🚀 Calculate Route", type="primary", use_container_width=True)
    
    # Clear button
    if st.session_state.route_data is not None:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.route_data = None
            st.session_state.map_obj = None
            st.rerun()

# Main area
if calculate or st.session_state.route_data is not None:
    # Only calculate if button was clicked, otherwise use cached data
    if calculate:
        with st.spinner("Downloading map data..."):
            try:
                # Download road network
                G = ox.graph_from_place(place, network_type="drive")
                st.success(f"✅ Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")
                
                # Find nearest nodes
                orig_node = ox.nearest_nodes(G, X=orig_lon, Y=orig_lat)
                dest_node = ox.nearest_nodes(G, X=dest_lon, Y=dest_lat)
                
                # Calculate route
                with st.spinner("Calculating shortest path..."):
                    if algorithm == "A*":
                        route = nx.astar_path(G, source=orig_node, target=dest_node, weight="length")
                    else:
                        route = nx.shortest_path(G, source=orig_node, target=dest_node, weight="length")
                
                # Calculate route statistics
                route_length = sum(
                    G[route[i]][route[i+1]][0]['length'] 
                    for i in range(len(route) - 1)
                )
                
                # Get route coordinates
                route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
                
                # Center point
                center_lat = sum(coord[0] for coord in route_coords) / len(route_coords)
                center_lon = sum(coord[1] for coord in route_coords) / len(route_coords)
                
                # Create folium map
                m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
                
                # Add route
                folium.PolyLine(
                    route_coords,
                    color='red',
                    weight=5,
                    opacity=0.8,
                    popup="Route"
                ).add_to(m)
                
                # Add origin marker
                folium.Marker(
                    location=(G.nodes[orig_node]['y'], G.nodes[orig_node]['x']),
                    popup='Origin',
                    icon=folium.Icon(color='green', icon='play', prefix='fa')
                ).add_to(m)
                
                # Add destination marker
                folium.Marker(
                    location=(G.nodes[dest_node]['y'], G.nodes[dest_node]['x']),
                    popup='Destination',
                    icon=folium.Icon(color='blue', icon='stop', prefix='fa')
                ).add_to(m)
                
                # Store in session state
                st.session_state.route_data = {
                    'route_length': route_length,
                    'route_nodes': len(route),
                    'route_edges': len(route) - 1,
                    'route_coords': route_coords,
                    'orig_node': orig_node,
                    'dest_node': dest_node,
                    'G': G
                }
                st.session_state.map_obj = m
                st.session_state.map_rendered = False
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try adjusting the city name or coordinates")
                st.session_state.route_data = None
                st.session_state.map_obj = None
                st.session_state.map_rendered = False
    
    # Display cached results
    if st.session_state.route_data is not None:
        data = st.session_state.route_data
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Route Length", f"{data['route_length']/1000:.2f} km")
        with col2:
            st.metric("Number of Nodes", data['route_nodes'])
        with col3:
            st.metric("Edges Traversed", data['route_edges'])
        
        # Add street network option - use session state to prevent reruns
        show_streets = st.checkbox(
            "Show street network", 
            value=st.session_state.show_streets,
            key="streets_checkbox"
        )
        st.session_state.show_streets = show_streets
        
        # Use a container to isolate map rendering
        map_container = st.container()
        with map_container:
            if show_streets:
                # Recreate map with streets
                G = data['G']
                m = folium.Map(
                    location=[sum(coord[0] for coord in data['route_coords']) / len(data['route_coords']),
                             sum(coord[1] for coord in data['route_coords']) / len(data['route_coords'])],
                    zoom_start=14
                )
                
                edges = ox.convert.graph_to_gdfs(G, nodes=False)
                for idx, row in edges.head(1000).iterrows():  # Limit for performance
                    if row.geometry:
                        folium.PolyLine(
                            [(lat, lon) for lon, lat in zip(row.geometry.xy[0], row.geometry.xy[1])],
                            color='lightgray',
                            weight=1,
                            opacity=0.3
                        ).add_to(m)
                
                # Add route
                folium.PolyLine(
                    data['route_coords'],
                    color='red',
                    weight=5,
                    opacity=0.8,
                    popup="Route"
                ).add_to(m)
                
                # Add markers
                folium.Marker(
                    location=(G.nodes[data['orig_node']]['y'], G.nodes[data['orig_node']]['x']),
                    popup='Origin',
                    icon=folium.Icon(color='green', icon='play', prefix='fa')
                ).add_to(m)
                
                folium.Marker(
                    location=(G.nodes[data['dest_node']]['y'], G.nodes[data['dest_node']]['x']),
                    popup='Destination',
                    icon=folium.Icon(color='blue', icon='stop', prefix='fa')
                ).add_to(m)
                
                # Prevent reruns by ignoring map interactions
                st_folium(
                    m, 
                    width=1200, 
                    height=600, 
                    key="map_with_streets",
                    returned_objects=[]
                )
            else:
                # Display cached map
                if st.session_state.map_obj is not None:
                    # Prevent reruns by ignoring map interactions
                    st_folium(
                        st.session_state.map_obj, 
                        width=1200, 
                        height=600, 
                        key="map",
                        returned_objects=[]
                    )
else:
    st.info("👈 Enter your settings in the sidebar and click 'Calculate Route' to get started")
    
    # Show example map
    st.subheader("Example")
    example_map = folium.Map(location=[25.686, -100.316], zoom_start=12)
    st_folium(example_map, width=1200, height=400, returned_objects=[])


st.markdown("Written by Juan Pablo Gutierrez")