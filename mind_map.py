import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import json
import math
from typing import Dict, List, Tuple, Optional


class MindMapNode:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        node_id: str = None,
        color: str = "#3498db",
        node_type: str = "concept",
    ):
        self.x = x
        self.y = y
        self.text = text
        self.id = node_id or f"node_{id(self)}"
        self.color = color
        self.node_type = node_type
        self.width = 100
        self.height = 60
        self.selected = False
        self.connections = []  # List of connected node IDs

    def contains_point(self, x: float, y: float) -> bool:
        return (
            self.x - self.width / 2 <= x <= self.x + self.width / 2
            and self.y - self.height / 2 <= y <= self.y + self.height / 2
        )

    def get_connection_point(
        self, target_x: float, target_y: float
    ) -> Tuple[float, float]:
        # Calculate the point on the node's edge closest to the target
        dx = target_x - self.x
        dy = target_y - self.y

        if dx == 0 and dy == 0:
            return self.x, self.y

        # Calculate angle
        angle = math.atan2(dy, dx)

        # Calculate edge point
        edge_x = self.x + (self.width / 2) * math.cos(angle)
        edge_y = self.y + (self.height / 2) * math.sin(angle)

        return edge_x, edge_y

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "text": self.text,
            "color": self.color,
            "node_type": self.node_type,
            "connections": self.connections,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        node = cls(
            x=data["x"],
            y=data["y"],
            text=data["text"],
            node_id=data["id"],
            color=data.get("color", "#3498db"),
            node_type=data.get("node_type", "concept"),
        )
        node.connections = data.get("connections", [])
        return node


class MindMapConnection:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        connection_type: str = "related",
        color: str = "#95a5a6",
        label: str = "",
    ):
        self.source_id = source_id
        self.target_id = target_id
        self.connection_type = connection_type
        self.color = color
        self.label = label

    def to_dict(self) -> Dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "connection_type": self.connection_type,
            "color": self.color,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            connection_type=data.get("connection_type", "related"),
            color=data.get("color", "#95a5a6"),
            label=data.get("label", ""),
        )


class MindMapCanvas:
    def __init__(self, parent, width: int = 800, height: int = 600):
        self.parent = parent
        self.width = width
        self.height = height

        # Create canvas with scrollbars
        self.setup_canvas()

        # Mind map data
        self.nodes = {}  # Dict[str, MindMapNode]
        self.connections = {}  # Dict[str, MindMapConnection]

        # Interaction state
        self.selected_node = None
        self.dragging_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting_mode = False
        self.connection_source = None

        # Bind events
        self.bind_events()

    def setup_canvas(self):
        # Main frame
        self.frame = ttk_bs.Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=True)

        # Canvas with scrollbars
        self.canvas = tk.Canvas(
            self.frame,
            width=self.width,
            height=self.height,
            bg="white",
            scrollregion=(0, 0, 2000, 2000),
        )

        # Scrollbars
        v_scrollbar = ttk_bs.Scrollbar(
            self.frame, orient=VERTICAL, command=self.canvas.yview
        )
        h_scrollbar = ttk_bs.Scrollbar(
            self.frame, orient=HORIZONTAL, command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Toolbar
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = ttk_bs.Frame(self.parent)
        toolbar.pack(fill=X, pady=(0, 5))

        # Tool buttons
        ttk_bs.Button(
            toolbar,
            text="➕ Add Node",
            command=self.add_node_mode,
            style="Success.Outline.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            toolbar,
            text="🔗 Connect",
            command=self.toggle_connection_mode,
            style="Info.Outline.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            toolbar,
            text="🗑️ Delete",
            command=self.delete_selected,
            style="Danger.Outline.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, padx=10, fill=Y)

        ttk_bs.Button(
            toolbar,
            text="🎨 Color",
            command=self.change_node_color,
            style="Warning.Outline.TButton",
        ).pack(side=LEFT, padx=2)

        ttk_bs.Button(
            toolbar,
            text="💾 Save",
            command=self.save_mind_map,
            style="Secondary.TButton",
        ).pack(side=RIGHT, padx=2)

        ttk_bs.Button(
            toolbar,
            text="📂 Load",
            command=self.load_mind_map,
            style="Secondary.TButton",
        ).pack(side=RIGHT, padx=2)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind(
            "<Button-3>", self.on_right_click
        )  # Right click for context menu

    def on_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        # Find clicked node
        clicked_node = None
        for node in self.nodes.values():
            if node.contains_point(x, y):
                clicked_node = node
                break

        if self.connecting_mode and self.connection_source:
            # Complete connection
            if clicked_node and clicked_node != self.connection_source:
                self.create_connection(self.connection_source, clicked_node)
            self.connecting_mode = False
            self.connection_source = None
            self.canvas.config(cursor="")

        elif clicked_node:
            # Select and prepare for dragging
            self.select_node(clicked_node)
            self.dragging_node = clicked_node
            self.drag_start_x = x - clicked_node.x
            self.drag_start_y = y - clicked_node.y

        else:
            # Deselect all
            self.select_node(None)

        self.redraw()

    def on_drag(self, event):
        if self.dragging_node:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self.dragging_node.x = x - self.drag_start_x
            self.dragging_node.y = y - self.drag_start_y
            self.redraw()

    def on_release(self, event):
        self.dragging_node = None

    def on_double_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        # Find double-clicked node
        clicked_node = None
        for node in self.nodes.values():
            if node.contains_point(x, y):
                clicked_node = node
                break

        if clicked_node:
            self.edit_node_text(clicked_node)
        else:
            self.create_node(x, y)

    def on_right_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        # Find right-clicked node
        clicked_node = None
        for node in self.nodes.values():
            if node.contains_point(x, y):
                clicked_node = node
                break

        if clicked_node:
            self.show_context_menu(event, clicked_node)

    def show_context_menu(self, event, node):
        context_menu = tk.Menu(self.canvas, tearoff=0)
        context_menu.add_command(
            label="Edit Text", command=lambda: self.edit_node_text(node)
        )
        context_menu.add_command(
            label="Change Color", command=lambda: self.change_node_color(node)
        )
        context_menu.add_separator()
        context_menu.add_command(label="Delete", command=lambda: self.delete_node(node))

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def create_node(self, x: float, y: float, text: str = "New Node") -> MindMapNode:
        node = MindMapNode(x, y, text)
        self.nodes[node.id] = node
        self.redraw()
        return node

    def delete_node(self, node: MindMapNode):
        # Remove connections
        connections_to_remove = []
        for conn_id, conn in self.connections.items():
            if conn.source_id == node.id or conn.target_id == node.id:
                connections_to_remove.append(conn_id)

        for conn_id in connections_to_remove:
            del self.connections[conn_id]

        # Remove node
        if node.id in self.nodes:
            del self.nodes[node.id]

        if self.selected_node == node:
            self.selected_node = None

        self.redraw()

    def create_connection(
        self, source: MindMapNode, target: MindMapNode
    ) -> MindMapConnection:
        conn_id = f"{source.id}_{target.id}"
        if conn_id not in self.connections:
            connection = MindMapConnection(source.id, target.id)
            self.connections[conn_id] = connection

            # Add to node connections lists
            if target.id not in source.connections:
                source.connections.append(target.id)
            if source.id not in target.connections:
                target.connections.append(source.id)

        self.redraw()
        return self.connections[conn_id]

    def select_node(self, node: Optional[MindMapNode]):
        if self.selected_node:
            self.selected_node.selected = False
        self.selected_node = node
        if node:
            node.selected = True

    def edit_node_text(self, node: MindMapNode):
        dialog = NodeEditDialog(self.parent, node.text)
        if dialog.result:
            node.text = dialog.result
            self.redraw()

    def change_node_color(self, node: MindMapNode = None):
        target_node = node or self.selected_node
        if not target_node:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return

        color = colorchooser.askcolor(
            title="Choose Node Color", initialcolor=target_node.color
        )
        if color[1]:  # If user didn't cancel
            target_node.color = color[1]
            self.redraw()

    def add_node_mode(self):
        messagebox.showinfo(
            "Add Node", "Double-click anywhere on the canvas to add a new node."
        )

    def toggle_connection_mode(self):
        if not self.selected_node:
            messagebox.showwarning(
                "No Selection", "Please select a node first, then click this button."
            )
            return

        self.connecting_mode = True
        self.connection_source = self.selected_node
        self.canvas.config(cursor="crosshair")
        messagebox.showinfo(
            "Connection Mode", "Click on another node to create a connection."
        )

    def delete_selected(self):
        if self.selected_node:
            if messagebox.askyesno(
                "Confirm Delete", f"Delete node '{self.selected_node.text}'?"
            ):
                self.delete_node(self.selected_node)
        else:
            messagebox.showwarning("No Selection", "Please select a node to delete.")

    def redraw(self):
        self.canvas.delete("all")

        # Draw connections first (so they appear behind nodes)
        for connection in self.connections.values():
            self.draw_connection(connection)

        # Draw nodes
        for node in self.nodes.values():
            self.draw_node(node)

    def draw_node(self, node: MindMapNode):
        x1 = node.x - node.width / 2
        y1 = node.y - node.height / 2
        x2 = node.x + node.width / 2
        y2 = node.y + node.height / 2

        # Node shape
        fill_color = node.color
        outline_color = "#2c3e50" if node.selected else "#34495e"
        outline_width = 3 if node.selected else 1

        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=fill_color,
            outline=outline_color,
            width=outline_width,
            tags=f"node_{node.id}",
        )

        # Node text
        self.canvas.create_text(
            node.x,
            node.y,
            text=node.text,
            font=("Helvetica", 10, "bold"),
            fill="white" if self.is_dark_color(node.color) else "black",
            width=node.width - 10,
            tags=f"text_{node.id}",
        )

    def draw_connection(self, connection: MindMapConnection):
        source_node = self.nodes.get(connection.source_id)
        target_node = self.nodes.get(connection.target_id)

        if not source_node or not target_node:
            return

        # Get connection points on node edges
        source_x, source_y = source_node.get_connection_point(
            target_node.x, target_node.y
        )
        target_x, target_y = target_node.get_connection_point(
            source_node.x, source_node.y
        )

        # Draw line
        self.canvas.create_line(
            source_x,
            source_y,
            target_x,
            target_y,
            fill=connection.color,
            width=2,
            arrow=tk.LAST,
            arrowshape=(10, 12, 5),
            tags=f"connection_{connection.source_id}_{connection.target_id}",
        )

        # Draw label if exists
        if connection.label:
            mid_x = (source_x + target_x) / 2
            mid_y = (source_y + target_y) / 2
            self.canvas.create_text(
                mid_x,
                mid_y,
                text=connection.label,
                font=("Helvetica", 8),
                fill=connection.color,
                tags=f"label_{connection.source_id}_{connection.target_id}",
            )

    def is_dark_color(self, color: str) -> bool:
        # Simple dark color detection
        if color.startswith("#"):
            color = color[1:]
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128
        except:
            return False

    def save_mind_map(self):
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": [conn.to_dict() for conn in self.connections.values()],
        }

        # For now, just save to a file (in a real app, this would save to database)
        try:
            with open("mind_map.json", "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Mind map saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save mind map: {str(e)}")

    def load_mind_map(self):
        try:
            with open("mind_map.json", "r") as f:
                data = json.load(f)

            # Clear current data
            self.nodes.clear()
            self.connections.clear()

            # Load nodes
            for node_data in data.get("nodes", []):
                node = MindMapNode.from_dict(node_data)
                self.nodes[node.id] = node

            # Load connections
            for conn_data in data.get("connections", []):
                conn = MindMapConnection.from_dict(conn_data)
                conn_id = f"{conn.source_id}_{conn.target_id}"
                self.connections[conn_id] = conn

            self.redraw()
            messagebox.showinfo("Success", "Mind map loaded successfully!")

        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "No saved mind map found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mind map: {str(e)}")

    def get_map_data(self) -> Dict:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": [conn.to_dict() for conn in self.connections.values()],
        }

    def load_map_data(self, data: Dict):
        self.nodes.clear()
        self.connections.clear()

        # Load nodes
        for node_data in data.get("nodes", []):
            node = MindMapNode.from_dict(node_data)
            self.nodes[node.id] = node

        # Load connections
        for conn_data in data.get("connections", []):
            conn = MindMapConnection.from_dict(conn_data)
            conn_id = f"{conn.source_id}_{conn.target_id}"
            self.connections[conn_id] = conn

        self.redraw()


class NodeEditDialog:
    def __init__(self, parent, initial_text: str = ""):
        self.result = None

        # Create dialog
        self.dialog = ttk_bs.Toplevel(parent)
        self.dialog.title("Edit Node")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create form
        main_frame = ttk_bs.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk_bs.Label(main_frame, text="Node Text:").pack(anchor=W)

        self.text_var = tk.StringVar(value=initial_text)
        text_entry = ttk_bs.Entry(main_frame, textvariable=self.text_var, width=30)
        text_entry.pack(fill=X, pady=(5, 15))
        text_entry.focus_set()
        text_entry.select_range(0, tk.END)

        # Buttons
        btn_frame = ttk_bs.Frame(main_frame)
        btn_frame.pack(fill=X)

        ttk_bs.Button(
            btn_frame, text="Cancel", command=self.cancel, style="Secondary.TButton"
        ).pack(side=RIGHT, padx=(10, 0))

        ttk_bs.Button(
            btn_frame, text="OK", command=self.ok, style="Success.TButton"
        ).pack(side=RIGHT)

        # Bind Enter key
        text_entry.bind("<Return>", lambda e: self.ok())

        # Wait for dialog
        parent.wait_window(self.dialog)

    def ok(self):
        self.result = self.text_var.get().strip()
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


class MindMapWidget:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk_bs.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(
            header_frame, text="🧠 Mind Map Creator", font=("Helvetica", 16, "bold")
        ).pack(side=LEFT)

        # Instructions
        instructions = ttk_bs.Label(
            header_frame,
            text="Double-click to create nodes • Select and click 'Connect' to link nodes • Right-click for options",
            foreground="gray",
        )
        instructions.pack(side=RIGHT)

        # Mind map canvas
        self.mind_map = MindMapCanvas(self.main_frame, width=800, height=600)

        # Add some sample nodes
        self.add_sample_nodes()

    def add_sample_nodes(self):
        # Create a sample mind map
        center_node = self.mind_map.create_node(400, 300, "Learning Topic")
        center_node.color = "#e74c3c"

        # Sub-topics
        subtopics = [
            (300, 200, "Concepts", "#3498db"),
            (500, 200, "Applications", "#2ecc71"),
            (300, 400, "Examples", "#f39c12"),
            (500, 400, "Resources", "#9b59b6"),
        ]

        for x, y, text, color in subtopics:
            node = self.mind_map.create_node(x, y, text)
            node.color = color
            self.mind_map.create_connection(center_node, node)

        self.mind_map.redraw()


# Example usage
if __name__ == "__main__":
    root = ttk_bs.Window(themename="superhero")
    root.title("Mind Map Demo")
    root.geometry("1000x700")

    widget = MindMapWidget(root)

    root.mainloop()
