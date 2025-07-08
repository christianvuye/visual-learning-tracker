import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
import json


class KnowledgeGraphWidget:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.graph = nx.Graph()
        self.node_positions = {}
        self.selected_node = None
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Header with controls
        self.create_header()

        # Create paned window for graph and controls
        self.paned_window = ttk_bs.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Left panel - Graph visualization
        self.create_graph_panel()

        # Right panel - Controls and node details
        self.create_control_panel()

        # Load initial data
        self.load_sample_graph()

    def create_header(self):
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, padx=20, pady=20)

        ttk_bs.Label(
            header_frame, text="🔗 Knowledge Graph", font=("Helvetica", 18, "bold")
        ).pack(side=LEFT)

        # Control buttons
        control_frame = ttk_bs.Frame(header_frame)
        control_frame.pack(side=RIGHT)

        ttk_bs.Button(
            control_frame,
            text="🆕 New Graph",
            command=self.new_graph,
            style="Success.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            control_frame,
            text="💾 Save Graph",
            command=self.save_graph,
            style="Info.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            control_frame,
            text="📂 Load Graph",
            command=self.load_graph,
            style="Warning.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            control_frame,
            text="➕ Add Node",
            command=self.add_node_dialog,
            style="Secondary.TButton",
        ).pack(side=LEFT, padx=2)

    def create_graph_panel(self):
        # Graph visualization frame
        graph_frame = ttk_bs.Frame(self.paned_window)
        self.paned_window.add(graph_frame, weight=3)

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.fig.patch.set_facecolor("#2c3e50")  # Dark background

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#34495e")
        self.ax.set_title(
            "Knowledge Graph Visualization",
            color="white",
            fontsize=14,
            fontweight="bold",
        )

        # Remove axes for cleaner look
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        # Bind click events
        self.canvas.mpl_connect("button_press_event", self.on_node_click)

    def create_control_panel(self):
        # Control panel frame
        control_frame = ttk_bs.Frame(self.paned_window, width=300)
        self.paned_window.add(control_frame, weight=1)

        # Node details section
        self.create_node_details(control_frame)

        # Graph statistics
        self.create_graph_stats(control_frame)

        # Layout controls
        self.create_layout_controls(control_frame)

        # Connection tools
        self.create_connection_tools(control_frame)

    def create_node_details(self, parent):
        details_frame = ttk_bs.LabelFrame(parent, text="Node Details", padding=15)
        details_frame.pack(fill=X, padx=10, pady=10)

        # Selected node info
        self.node_title_label = ttk_bs.Label(
            details_frame, text="No node selected", font=("Helvetica", 12, "bold")
        )
        self.node_title_label.pack(anchor=W)

        self.node_type_label = ttk_bs.Label(details_frame, text="")
        self.node_type_label.pack(anchor=W, pady=(5, 0))

        self.node_connections_label = ttk_bs.Label(details_frame, text="")
        self.node_connections_label.pack(anchor=W, pady=(5, 0))

        # Node description
        ttk_bs.Label(
            details_frame, text="Description:", font=("Helvetica", 10, "bold")
        ).pack(anchor=W, pady=(10, 5))

        self.node_description = tk.Text(
            details_frame, height=4, width=30, font=("Helvetica", 9), state="disabled"
        )
        self.node_description.pack(fill=X)

        # Action buttons
        btn_frame = ttk_bs.Frame(details_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk_bs.Button(
            btn_frame,
            text="Edit",
            command=self.edit_selected_node,
            style="Info.Outline.TButton",
            width=10,
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            btn_frame,
            text="Delete",
            command=self.delete_selected_node,
            style="Danger.Outline.TButton",
            width=10,
        ).pack(side=LEFT, padx=2)

    def create_graph_stats(self, parent):
        stats_frame = ttk_bs.LabelFrame(parent, text="Graph Statistics", padding=15)
        stats_frame.pack(fill=X, padx=10, pady=(0, 10))

        # Statistics labels
        self.stats_labels = {}
        stats_items = [
            ("Nodes", "nodes"),
            ("Connections", "edges"),
            ("Clusters", "clusters"),
            ("Density", "density"),
        ]

        for label_text, key in stats_items:
            stat_item = ttk_bs.Frame(stats_frame)
            stat_item.pack(fill=X, pady=2)

            ttk_bs.Label(stat_item, text=f"{label_text}:", width=12).pack(side=LEFT)

            value_label = ttk_bs.Label(
                stat_item, text="0", font=("Helvetica", 10, "bold")
            )
            value_label.pack(side=LEFT)
            self.stats_labels[key] = value_label

    def create_layout_controls(self, parent):
        layout_frame = ttk_bs.LabelFrame(parent, text="Layout Options", padding=15)
        layout_frame.pack(fill=X, padx=10, pady=(0, 10))

        # Layout algorithm selection
        ttk_bs.Label(layout_frame, text="Layout Algorithm:").pack(anchor=W)

        self.layout_var = tk.StringVar(value="spring")
        layout_combo = ttk_bs.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["spring", "circular", "random", "shell", "spectral"],
            state="readonly",
        )
        layout_combo.pack(fill=X, pady=(5, 10))
        layout_combo.bind("<<ComboboxSelected>>", self.change_layout)

        # Node size control
        ttk_bs.Label(layout_frame, text="Node Size:").pack(anchor=W)

        self.node_size_var = tk.IntVar(value=300)
        node_size_scale = ttk_bs.Scale(
            layout_frame,
            from_=100,
            to=1000,
            variable=self.node_size_var,
            orient=HORIZONTAL,
            command=self.update_node_size,
        )
        node_size_scale.pack(fill=X, pady=(5, 10))

        # Edge thickness control
        ttk_bs.Label(layout_frame, text="Edge Thickness:").pack(anchor=W)

        self.edge_width_var = tk.DoubleVar(value=1.0)
        edge_width_scale = ttk_bs.Scale(
            layout_frame,
            from_=0.5,
            to=5.0,
            variable=self.edge_width_var,
            orient=HORIZONTAL,
            command=self.update_edge_width,
        )
        edge_width_scale.pack(fill=X, pady=(5, 0))

    def create_connection_tools(self, parent):
        connect_frame = ttk_bs.LabelFrame(parent, text="Connection Tools", padding=15)
        connect_frame.pack(fill=X, padx=10, pady=(0, 10))

        # Connection type selection
        ttk_bs.Label(connect_frame, text="Connection Type:").pack(anchor=W)

        self.connection_type_var = tk.StringVar(value="related")
        connection_combo = ttk_bs.Combobox(
            connect_frame,
            textvariable=self.connection_type_var,
            values=["related", "prerequisite", "applies_to", "example_of", "part_of"],
            state="readonly",
        )
        connection_combo.pack(fill=X, pady=(5, 10))

        # Action buttons
        ttk_bs.Button(
            connect_frame,
            text="🔗 Connect Nodes",
            command=self.connect_nodes_dialog,
            style="Warning.TButton",
        ).pack(fill=X, pady=2)

        ttk_bs.Button(
            connect_frame,
            text="📊 Analyze Graph",
            command=self.analyze_graph,
            style="Info.TButton",
        ).pack(fill=X, pady=2)

    def load_sample_graph(self):
        """Load a sample knowledge graph for demonstration"""
        # Clear existing graph
        self.graph.clear()

        # Add sample nodes for a programming course
        nodes = [
            ("Variables", "concept", "Basic data storage in programming"),
            ("Data Types", "concept", "Integer, String, Boolean, etc."),
            ("Functions", "concept", "Reusable blocks of code"),
            ("Loops", "concept", "Repetitive execution structures"),
            ("Conditionals", "concept", "Decision-making in code"),
            ("Arrays", "concept", "Collections of related data"),
            ("Objects", "concept", "Data structures with methods"),
            ("Classes", "concept", "Templates for creating objects"),
            ("Inheritance", "concept", "Extending existing classes"),
            ("Polymorphism", "concept", "Multiple forms of the same interface"),
        ]

        for title, node_type, description in nodes:
            self.graph.add_node(title, node_type=node_type, description=description)

        # Add relationships
        connections = [
            ("Variables", "Data Types", "has"),
            ("Functions", "Variables", "uses"),
            ("Loops", "Conditionals", "often_contains"),
            ("Arrays", "Variables", "type_of"),
            ("Objects", "Variables", "type_of"),
            ("Classes", "Objects", "creates"),
            ("Classes", "Functions", "contains"),
            ("Inheritance", "Classes", "extends"),
            ("Polymorphism", "Inheritance", "builds_on"),
            ("Functions", "Data Types", "returns"),
        ]

        for source, target, relation in connections:
            self.graph.add_edge(source, target, relation=relation)

        # Draw the graph
        self.draw_graph()
        self.update_statistics()

    def draw_graph(self):
        """Draw the knowledge graph using matplotlib"""
        self.ax.clear()

        if len(self.graph.nodes()) == 0:
            self.ax.text(
                0.5,
                0.5,
                'No nodes in graph\nClick "Add Node" to get started',
                ha="center",
                va="center",
                transform=self.ax.transAxes,
                color="white",
                fontsize=12,
            )
            self.canvas.draw()
            return

        # Generate layout
        layout_type = self.layout_var.get()
        if layout_type == "spring":
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(self.graph)
        elif layout_type == "random":
            pos = nx.random_layout(self.graph)
        elif layout_type == "shell":
            pos = nx.shell_layout(self.graph)
        else:  # spectral
            pos = nx.spectral_layout(self.graph)

        self.node_positions = pos

        # Draw edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            ax=self.ax,
            edge_color="#7f8c8d",
            width=self.edge_width_var.get(),
            alpha=0.6,
        )

        # Draw nodes with different colors based on type
        node_colors = []
        node_types = nx.get_node_attributes(self.graph, "node_type")

        type_colors = {
            "concept": "#3498db",
            "skill": "#2ecc71",
            "tool": "#e74c3c",
            "theory": "#9b59b6",
            "practice": "#f39c12",
        }

        for node in self.graph.nodes():
            node_type = node_types.get(node, "concept")
            node_colors.append(type_colors.get(node_type, "#3498db"))

        # Highlight selected node
        if self.selected_node and self.selected_node in self.graph.nodes():
            node_colors[list(self.graph.nodes()).index(self.selected_node)] = "#e67e22"

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            ax=self.ax,
            node_color=node_colors,
            node_size=self.node_size_var.get(),
            alpha=0.8,
        )

        # Draw labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            ax=self.ax,
            font_size=8,
            font_color="white",
            font_weight="bold",
        )

        # Style the plot
        self.ax.set_facecolor("#34495e")
        self.ax.set_title(
            "Knowledge Graph Visualization",
            color="white",
            fontsize=14,
            fontweight="bold",
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.canvas.draw()

    def on_node_click(self, event):
        """Handle node selection on click"""
        if event.inaxes != self.ax or not self.node_positions:
            return

        # Find closest node to click
        click_pos = (event.xdata, event.ydata)
        if click_pos[0] is None or click_pos[1] is None:
            return

        min_dist = float("inf")
        closest_node = None

        for node, pos in self.node_positions.items():
            dist = np.sqrt((pos[0] - click_pos[0]) ** 2 + (pos[1] - click_pos[1]) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest_node = node

        # Select node if click is close enough
        if min_dist < 0.1:  # Adjust threshold as needed
            self.selected_node = closest_node
            self.update_node_details()
            self.draw_graph()  # Redraw to show selection

    def update_node_details(self):
        """Update the node details panel"""
        if not self.selected_node:
            self.node_title_label.config(text="No node selected")
            self.node_type_label.config(text="")
            self.node_connections_label.config(text="")
            self.node_description.config(state="normal")
            self.node_description.delete(1.0, tk.END)
            self.node_description.config(state="disabled")
            return

        # Update labels
        self.node_title_label.config(text=self.selected_node)

        node_data = self.graph.nodes[self.selected_node]
        node_type = node_data.get("node_type", "Unknown")
        self.node_type_label.config(text=f"Type: {node_type}")

        connections = list(self.graph.neighbors(self.selected_node))
        self.node_connections_label.config(text=f"Connections: {len(connections)}")

        # Update description
        description = node_data.get("description", "No description available.")
        self.node_description.config(state="normal")
        self.node_description.delete(1.0, tk.END)
        self.node_description.insert(1.0, description)
        self.node_description.config(state="disabled")

    def update_statistics(self):
        """Update graph statistics"""
        num_nodes = len(self.graph.nodes())
        num_edges = len(self.graph.edges())

        # Calculate number of connected components (clusters)
        num_clusters = (
            nx.number_connected_components(self.graph) if num_nodes > 0 else 0
        )

        # Calculate density
        density = nx.density(self.graph) if num_nodes > 1 else 0

        # Update labels
        self.stats_labels["nodes"].config(text=str(num_nodes))
        self.stats_labels["edges"].config(text=str(num_edges))
        self.stats_labels["clusters"].config(text=str(num_clusters))
        self.stats_labels["density"].config(text=f"{density:.2f}")

    def change_layout(self, event=None):
        """Change graph layout algorithm"""
        self.draw_graph()

    def update_node_size(self, value=None):
        """Update node size"""
        self.draw_graph()

    def update_edge_width(self, value=None):
        """Update edge thickness"""
        self.draw_graph()

    def add_node_dialog(self):
        """Open dialog to add new node"""
        dialog = AddNodeDialog(self.parent)
        if dialog.result:
            title, node_type, description = dialog.result
            self.graph.add_node(title, node_type=node_type, description=description)
            self.draw_graph()
            self.update_statistics()

    def connect_nodes_dialog(self):
        """Open dialog to connect two nodes"""
        if len(self.graph.nodes()) < 2:
            messagebox.showwarning(
                "Insufficient Nodes", "Need at least 2 nodes to create connections."
            )
            return

        dialog = ConnectNodesDialog(self.parent, list(self.graph.nodes()))
        if dialog.result:
            source, target, relation = dialog.result
            if source != target:
                self.graph.add_edge(source, target, relation=relation)
                self.draw_graph()
                self.update_statistics()

    def edit_selected_node(self):
        """Edit the selected node"""
        if not self.selected_node:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return

        node_data = self.graph.nodes[self.selected_node]
        dialog = EditNodeDialog(self.parent, self.selected_node, node_data)
        if dialog.result:
            title, node_type, description = dialog.result
            # Update node data
            self.graph.nodes[self.selected_node]["node_type"] = node_type
            self.graph.nodes[self.selected_node]["description"] = description

            # If title changed, need to rename the node
            if title != self.selected_node:
                self.graph = nx.relabel_nodes(self.graph, {self.selected_node: title})
                self.selected_node = title

            self.draw_graph()
            self.update_node_details()
            self.update_statistics()

    def delete_selected_node(self):
        """Delete the selected node"""
        if not self.selected_node:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return

        if messagebox.askyesno(
            "Confirm Delete", f"Delete node '{self.selected_node}'?"
        ):
            self.graph.remove_node(self.selected_node)
            self.selected_node = None
            self.update_node_details()
            self.draw_graph()
            self.update_statistics()

    def analyze_graph(self):
        """Analyze the graph and show insights"""
        if len(self.graph.nodes()) == 0:
            messagebox.showinfo("Analysis", "No nodes to analyze.")
            return

        analysis = []

        # Basic metrics
        num_nodes = len(self.graph.nodes())
        num_edges = len(self.graph.edges())
        density = nx.density(self.graph)

        analysis.append(
            f"Graph contains {num_nodes} concepts with {num_edges} connections."
        )
        analysis.append(f"Graph density: {density:.2f} (0=sparse, 1=complete)")

        # Find central nodes
        if num_nodes > 1:
            centrality = nx.degree_centrality(self.graph)
            most_central = max(centrality, key=centrality.get)
            analysis.append(f"Most central concept: '{most_central}' (high importance)")

        # Find isolated nodes
        isolated = list(nx.isolates(self.graph))
        if isolated:
            analysis.append(
                f"Isolated concepts: {', '.join(isolated)} (need more connections)"
            )

        # Connected components
        components = list(nx.connected_components(self.graph))
        if len(components) > 1:
            analysis.append(f"Graph has {len(components)} separate clusters")

        messagebox.showinfo("Graph Analysis", "\n\n".join(analysis))

    def load_course_graph(self):
        """Load knowledge graph for a specific course"""
        courses = self.db.get_courses()
        if not courses:
            messagebox.showinfo("No Courses", "Create some courses first!")
            return
        messagebox.showinfo(
            "Load Course", "Course-specific knowledge graphs coming soon!"
        )

    def refresh_graph(self):
        """Refresh the graph display"""
        self.draw_graph()
        self.update_statistics()

    def new_graph(self):
        """Create a new empty graph"""
        if len(self.graph.nodes()) > 0:
            if not messagebox.askyesno(
                "New Graph", "This will clear the current graph. Continue?"
            ):
                return

        self.graph.clear()
        self.selected_node = None
        self.node_positions = {}
        self.draw_graph()
        self.update_statistics()
        self.update_node_details()
        messagebox.showinfo("New Graph", "Created new empty knowledge graph.")

    def save_graph(self):
        """Save the current graph to a JSON file"""
        if len(self.graph.nodes()) == 0:
            messagebox.showwarning("Empty Graph", "No nodes to save.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Knowledge Graph",
        )

        if filename:
            try:
                # Convert graph to JSON-serializable format
                graph_data = {
                    "nodes": [
                        {
                            "id": node,
                            "node_type": self.graph.nodes[node].get(
                                "node_type", "concept"
                            ),
                            "description": self.graph.nodes[node].get(
                                "description", ""
                            ),
                        }
                        for node in self.graph.nodes()
                    ],
                    "edges": [
                        {
                            "source": edge[0],
                            "target": edge[1],
                            "relation": self.graph.edges[edge].get(
                                "relation", "related"
                            ),
                        }
                        for edge in self.graph.edges()
                    ],
                }

                with open(filename, "w") as f:
                    json.dump(graph_data, f, indent=2)

                messagebox.showinfo("Success", f"Graph saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {str(e)}")

    def load_graph(self):
        """Load a graph from a JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Knowledge Graph",
        )

        if filename:
            try:
                with open(filename, "r") as f:
                    graph_data = json.load(f)

                # Clear current graph
                self.graph.clear()
                self.selected_node = None

                # Load nodes
                for node_info in graph_data.get("nodes", []):
                    self.graph.add_node(
                        node_info["id"],
                        node_type=node_info.get("node_type", "concept"),
                        description=node_info.get("description", ""),
                    )

                # Load edges
                for edge_info in graph_data.get("edges", []):
                    self.graph.add_edge(
                        edge_info["source"],
                        edge_info["target"],
                        relation=edge_info.get("relation", "related"),
                    )

                self.draw_graph()
                self.update_statistics()
                self.update_node_details()
                messagebox.showinfo("Success", f"Graph loaded from {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load graph: {str(e)}")


class AddNodeDialog:
    def __init__(self, parent):
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Add Knowledge Node")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_form()

        # Wait for dialog
        parent.wait_window(self.dialog)

    def create_form(self):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(
            main_frame, text="Add Knowledge Node", font=("Helvetica", 14, "bold")
        ).pack(pady=(0, 20))

        # Title
        ttk_bs.Label(main_frame, text="Concept Title:").pack(anchor=W)
        self.title_var = tk.StringVar()
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=40).pack(
            fill=X, pady=(5, 15)
        )

        # Type
        ttk_bs.Label(main_frame, text="Node Type:").pack(anchor=W)
        self.type_var = tk.StringVar(value="concept")
        type_combo = ttk_bs.Combobox(
            main_frame,
            textvariable=self.type_var,
            values=["concept", "skill", "tool", "theory", "practice"],
            state="readonly",
        )
        type_combo.pack(fill=X, pady=(5, 15))

        # Description
        ttk_bs.Label(main_frame, text="Description:").pack(anchor=W)
        self.description_text = tk.Text(main_frame, height=4, width=40)
        self.description_text.pack(fill=X, pady=(5, 20))

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame, text="Add Node", command=self.add_node, style="Success.TButton"
        ).pack(side=RIGHT)

    def add_node(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a concept title.")
            return

        node_type = self.type_var.get()
        description = self.description_text.get(1.0, tk.END).strip()

        self.result = (title, node_type, description)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


class ConnectNodesDialog:
    def __init__(self, parent, nodes):
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Connect Nodes")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_form(nodes)

        # Wait for dialog
        parent.wait_window(self.dialog)

    def create_form(self, nodes):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(
            main_frame, text="Connect Knowledge Nodes", font=("Helvetica", 14, "bold")
        ).pack(pady=(0, 20))

        # Source node
        ttk_bs.Label(main_frame, text="Source Node:").pack(anchor=W)
        self.source_var = tk.StringVar()
        source_combo = ttk_bs.Combobox(
            main_frame, textvariable=self.source_var, values=nodes, state="readonly"
        )
        source_combo.pack(fill=X, pady=(5, 15))

        # Target node
        ttk_bs.Label(main_frame, text="Target Node:").pack(anchor=W)
        self.target_var = tk.StringVar()
        target_combo = ttk_bs.Combobox(
            main_frame, textvariable=self.target_var, values=nodes, state="readonly"
        )
        target_combo.pack(fill=X, pady=(5, 15))

        # Relationship type
        ttk_bs.Label(main_frame, text="Relationship:").pack(anchor=W)
        self.relation_var = tk.StringVar(value="related")
        relation_combo = ttk_bs.Combobox(
            main_frame,
            textvariable=self.relation_var,
            values=["related", "prerequisite", "applies_to", "example_of", "part_of"],
            state="readonly",
        )
        relation_combo.pack(fill=X, pady=(5, 20))

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame, text="Connect", command=self.connect, style="Success.TButton"
        ).pack(side=RIGHT)

    def connect(self):
        source = self.source_var.get()
        target = self.target_var.get()
        relation = self.relation_var.get()

        if not source or not target:
            messagebox.showerror("Error", "Please select both source and target nodes.")
            return

        if source == target:
            messagebox.showerror("Error", "Source and target must be different nodes.")
            return

        self.result = (source, target, relation)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


class EditNodeDialog:
    def __init__(self, parent, current_title, node_data):
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Edit Knowledge Node")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_form(current_title, node_data)

        # Wait for dialog
        parent.wait_window(self.dialog)

    def create_form(self, current_title, node_data):
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(
            main_frame, text="Edit Knowledge Node", font=("Helvetica", 14, "bold")
        ).pack(pady=(0, 20))

        # Title
        ttk_bs.Label(main_frame, text="Concept Title:").pack(anchor=W)
        self.title_var = tk.StringVar(value=current_title)
        ttk_bs.Entry(main_frame, textvariable=self.title_var, width=40).pack(
            fill=X, pady=(5, 15)
        )

        # Type
        ttk_bs.Label(main_frame, text="Node Type:").pack(anchor=W)
        self.type_var = tk.StringVar(value=node_data.get("node_type", "concept"))
        type_combo = ttk_bs.Combobox(
            main_frame,
            textvariable=self.type_var,
            values=["concept", "skill", "tool", "theory", "practice"],
            state="readonly",
        )
        type_combo.pack(fill=X, pady=(5, 15))

        # Description
        ttk_bs.Label(main_frame, text="Description:").pack(anchor=W)
        self.description_text = tk.Text(main_frame, height=4, width=40)
        self.description_text.pack(fill=X, pady=(5, 20))
        self.description_text.insert(1.0, node_data.get("description", ""))

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame,
            text="Update Node",
            command=self.update_node,
            style="Success.TButton",
        ).pack(side=RIGHT)

    def update_node(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a concept title.")
            return

        node_type = self.type_var.get()
        description = self.description_text.get(1.0, tk.END).strip()

        self.result = (title, node_type, description)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager

    root = ttk_bs.Window(themename="superhero")
    root.title("Knowledge Graph Demo")
    root.geometry("1200x800")

    db = DatabaseManager("test_knowledge.db")
    widget = KnowledgeGraphWidget(root, db)

    root.mainloop()
