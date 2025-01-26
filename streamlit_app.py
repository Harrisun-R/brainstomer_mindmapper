import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import json
from io import BytesIO

# Initialize session state for the mind map
if 'graph' not in st.session_state:
    st.session_state.graph = nx.DiGraph()
if 'flowchart_graph' not in st.session_state:
    st.session_state.flowchart_graph = nx.DiGraph()

# Sidebar for user input
st.sidebar.header("Mind Map Settings")

# Input fields for adding nodes
with st.sidebar.form("add_node_form"):
    node_name = st.text_input("Node Name:", "")
    node_color = st.color_picker("Node Color:", "#1f78b4")
    node_size = st.slider("Node Size:", 100, 1000, 300)
    submitted = st.form_submit_button("Add Node")
    
    if submitted and node_name:
        st.session_state.graph.add_node(node_name, color=node_color, size=node_size)
        st.sidebar.success(f"Node '{node_name}' added!")

# Input fields for adding edges
with st.sidebar.form("add_edge_form"):
    source_node = st.selectbox("Source Node:", options=list(st.session_state.graph.nodes), key="source")
    target_node = st.selectbox("Target Node:", options=list(st.session_state.graph.nodes), key="target")
    add_edge = st.form_submit_button("Add Connection")
    
    if add_edge and source_node != target_node:
        st.session_state.graph.add_edge(source_node, target_node)
        st.sidebar.success(f"Connection from '{source_node}' to '{target_node}' added!")

# Button to reset the mind map
if st.sidebar.button("Reset Map"):
    st.session_state.graph = nx.DiGraph()
    st.session_state.flowchart_graph = nx.DiGraph()
    st.sidebar.success("Mind map reset!")

# Export mind map as JSON
exported_json = json.dumps(
    nx.node_link_data(st.session_state.graph),
    indent=4
)

def save_json():
    return BytesIO(exported_json.encode())

st.sidebar.download_button(
    "Export Mind Map as JSON",
    save_json(),
    file_name="mind_map.json",
    mime="application/json"
)

# Import mind map from JSON
uploaded_file = st.sidebar.file_uploader("Import Mind Map JSON", type="json")
if uploaded_file:
    try:
        imported_data = json.load(uploaded_file)
        st.session_state.graph = nx.node_link_graph(imported_data)
        st.sidebar.success("Mind map imported successfully!")
    except Exception as e:
        st.sidebar.error("Error importing JSON: " + str(e))

# Main area to display the mind map
st.title("Brainstorming/Mind-Mapping Tool")
st.markdown("Use the sidebar to add nodes, connections, or import/export your mind map.")

if st.session_state.graph.nodes:
    # Draw the graph
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get node attributes
    node_colors = [data['color'] for _, data in st.session_state.graph.nodes(data=True)]
    node_sizes = [data['size'] for _, data in st.session_state.graph.nodes(data=True)]
    
    nx.draw(
        st.session_state.graph,
        with_labels=True,
        node_color=node_colors,
        node_size=node_sizes,
        ax=ax
    )
    
    st.pyplot(fig)

    # Download mind map as an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.download_button("Download Mind Map as Image", buffer, file_name="mind_map.png", mime="image/png")
else:
    st.info("No nodes in the mind map yet. Add some from the sidebar!")

# Generate flowchart from indented text
st.sidebar.header("Flowchart from Indented Text")
indented_text = st.sidebar.text_area("Enter indented text for flowchart generation:", "")
generate_flowchart = st.sidebar.button("Generate Flowchart")

if generate_flowchart and indented_text:
    st.session_state.flowchart_graph = nx.DiGraph()
    lines = indented_text.split("\n")
    parent_stack = []

    for line in lines:
        stripped = line.lstrip()
        depth = len(line) - len(stripped)

        while parent_stack and parent_stack[-1][1] >= depth:
            parent_stack.pop()

        current_node = stripped
        st.session_state.flowchart_graph.add_node(current_node)

        if parent_stack:
            parent_node = parent_stack[-1][0]
            st.session_state.flowchart_graph.add_edge(parent_node, current_node)

        parent_stack.append((current_node, depth))

    st.success("Flowchart generated successfully!")

if st.session_state.flowchart_graph.nodes:
    st.header("Generated Flowchart")
    fig, ax = plt.subplots(figsize=(10, 6))

    nx.draw(
        st.session_state.flowchart_graph,
        with_labels=True,
        node_size=3000,
        node_color="#ADD8E6",
        font_size=10,
        font_color="black",
        ax=ax
    )
    st.pyplot(fig)

    # Download flowchart as an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.download_button("Download Flowchart as Image", buffer, file_name="flowchart.png", mime="image/png")
