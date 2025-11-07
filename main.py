import sys
import os
import re
import time
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QListWidget, QListWidgetItem, 
                             QGroupBox, QSplitter, QMessageBox, QProgressBar,
                             QCheckBox, QOpenGLWidget, QSlider)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from OpenGL.GL import *
from OpenGL.GLU import *
from model_cache import get_cache


class MeshSimplifier:
    """Simple mesh simplification for LOD rendering"""
    
    @staticmethod
    def simplify_mesh(vertices, faces, reduction_factor=0.5):
        """
        Simplify mesh by reducing face count
        reduction_factor: 0.1 = 10% of faces, 0.5 = 50% of faces, 1.0 = 100% (no reduction)
        """
        if reduction_factor >= 1.0:
            return vertices, faces
        
        original_count = len(faces)
        
        # Calculate target number of faces
        target_faces = max(int(len(faces) * reduction_factor), 1)
        
        # Calculate step to achieve target
        step = max(len(faces) // target_faces, 1)
        
        # Keep every nth face
        simplified_faces = faces[::step]
        
        # Limit to target (in case step calculation was off)
        if len(simplified_faces) > target_faces:
            simplified_faces = simplified_faces[:target_faces]
        
        print(f"    Simplification: {original_count} → {len(simplified_faces)} faces (target: {target_faces}, step: {step})")
        
        # Get unique vertices used by simplified faces
        used_vertices = set()
        for face in simplified_faces:
            for idx in face:
                used_vertices.add(idx)
        
        # Create vertex mapping
        vertex_list = sorted(used_vertices)
        vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(vertex_list)}
        
        # Remap faces
        remapped_faces = []
        for face in simplified_faces:
            remapped_face = [vertex_map[idx] for idx in face]
            remapped_faces.append(remapped_face)
        
        # Get simplified vertices
        simplified_vertices = [vertices[idx] for idx in vertex_list]
        
        return simplified_vertices, remapped_faces
    
    @staticmethod
    def create_lod_levels(vertices, faces, levels=4):
        """Create multiple LOD levels"""
        lod_levels = []
        reductions = [1.0, 0.5, 0.25, 0.1]  # 100%, 50%, 25%, 10%
        
        for i in range(min(levels, len(reductions))):
            if i == 0:
                lod_levels.append((vertices, faces))
            else:
                simplified_verts, simplified_faces = MeshSimplifier.simplify_mesh(
                    vertices, faces, reductions[i]
                )
                lod_levels.append((simplified_verts, simplified_faces))
        
        return lod_levels


class OBJViewer(QOpenGLWidget):
    """OpenGL widget for 3D visualization with GPU-accelerated LOD support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.faces = []
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = -5.0
        self.last_pos = None
        self.auto_rotate = False
        
        # LOD system
        self.lod_levels = []
        self.current_lod = 0  # 0 = highest quality
        self.max_lod = 3
        self.auto_lod = True
        self.last_zoom = -5.0
        
        # GPU buffers (VBOs)
        self.vbo_data = []  # List of (vertex_buffer, index_buffer, index_count) for each LOD
        self.use_gpu = True
        
        # Multi-object display
        self.show_all_objects = False
        self.all_objects_data = {}  # {object_name: [(vbo_data), color, is_selected]}
        self.selected_objects = set()  # Set of selected object names
        
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        
        glClearColor(0.2, 0.2, 0.25, 1.0)
        
        # Enable client states for VBO rendering
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Draw model (either single object or all objects)
        if self.show_all_objects:
            if self.all_objects_data:
                self.draw_model()
        elif self.vertices and self.faces:
            self.draw_model()
            
    def draw_model(self):
        """GPU-accelerated rendering using VBOs"""
        if self.show_all_objects:
            self.draw_all_objects()
        else:
            self.draw_single_object()
    
    def draw_single_object(self):
        """Draw single selected object"""
        if not self.vbo_data or self.current_lod >= len(self.vbo_data):
            return
            
        vertex_data, normal_data, index_data, index_count = self.vbo_data[self.current_lod]
        
        if index_count == 0:
            return
        
        # Set color based on LOD level
        lod_colors = [
            (0.7, 0.7, 0.9),  # High quality - blueish
            (0.7, 0.8, 0.8),  # Medium quality - slightly greenish
            (0.8, 0.7, 0.7),  # Low quality - slightly reddish
            (0.8, 0.8, 0.6),  # Very low quality - yellowish
        ]
        
        color = lod_colors[min(self.current_lod, len(lod_colors) - 1)]
        glColor3f(*color)
        
        # Use GPU buffers for fast rendering
        glVertexPointer(3, GL_FLOAT, 0, vertex_data)
        glNormalPointer(GL_FLOAT, 0, normal_data)
        
        # Draw all triangles in one GPU call
        glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, index_data)
        
        # Optional: Draw wireframe (disable for better performance)
        if index_count < 100000:  # Only draw wireframe for smaller models
            glDisable(GL_LIGHTING)
            glColor3f(0.2, 0.2, 0.3)
            glLineWidth(0.5)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, index_data)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glEnable(GL_LIGHTING)
    
    def draw_all_objects(self):
        """Draw all objects with selection highlighting"""
        if not self.all_objects_data:
            return
        
        # Use current LOD level (respects user's LOD slider)
        lod = self.current_lod
        
        for obj_name, obj_data in self.all_objects_data.items():
            vbo_data_list, base_color, _ = obj_data
            
            if lod >= len(vbo_data_list):
                continue
                
            vertex_data, normal_data, index_data, index_count = vbo_data_list[lod]
            
            if index_count == 0:
                continue
            
            # Determine if object is selected
            is_selected = obj_name in self.selected_objects
            
            # Set color - dimmed for unselected, bright for selected
            if is_selected:
                color = (base_color[0] * 1.2, base_color[1] * 1.2, base_color[2] * 1.2)
            else:
                color = (base_color[0] * 0.5, base_color[1] * 0.5, base_color[2] * 0.5)
            
            glColor3f(*color)
            
            # Draw object
            glVertexPointer(3, GL_FLOAT, 0, vertex_data)
            glNormalPointer(GL_FLOAT, 0, normal_data)
            glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, index_data)
            
            # Draw thick border for selected objects
            if is_selected:
                glDisable(GL_LIGHTING)
                glColor3f(1.0, 0.5, 0.0)  # Orange highlight
                glLineWidth(4.0)  # Thick border
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, index_data)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glEnable(GL_LIGHTING)
        
    def set_model(self, vertices, faces):
        """Set the model to display with LOD generation and GPU buffer creation"""
        # Auto-center and scale
        if vertices:
            verts = np.array(vertices)
            center = np.mean(verts, axis=0)
            centered_verts = verts - center
            
            # Auto-scale
            max_dim = np.max(np.abs(centered_verts))
            if max_dim > 0:
                scaled_verts = centered_verts / max_dim * 2
            else:
                scaled_verts = centered_verts
            
            self.vertices = scaled_verts.tolist()
        else:
            self.vertices = vertices
            
        self.faces = faces
        
        # Generate LOD levels
        print(f"Generating LOD levels for {len(faces)} faces...")
        self.lod_levels = MeshSimplifier.create_lod_levels(self.vertices, self.faces)
        
        # Create GPU buffers for each LOD level
        print("Creating GPU buffers...")
        self.vbo_data = []
        
        for i, (verts, lod_faces) in enumerate(self.lod_levels):
            vertex_data, normal_data, index_data, index_count = self.create_gpu_buffers(verts, lod_faces)
            self.vbo_data.append((vertex_data, normal_data, index_data, index_count))
            print(f"  LOD {i}: {len(verts)} vertices, {len(lod_faces)} faces, {index_count} indices")
        
        self.current_lod = 0
        self.update()
    
    def create_gpu_buffers(self, vertices, faces):
        """Create GPU-optimized buffers from vertices and faces"""
        if not vertices or not faces:
            return (np.array([], dtype=np.float32), 
                    np.array([], dtype=np.float32), 
                    np.array([], dtype=np.uint32), 0)
        
        # Convert to numpy arrays for fast processing
        vertex_array = np.array(vertices, dtype=np.float32)
        
        # Build index buffer and calculate normals
        indices = []
        normals_list = [np.zeros(3, dtype=np.float32) for _ in range(len(vertices))]
        
        for face in faces:
            if len(face) >= 3:
                # Triangulate face (fan triangulation)
                for i in range(len(face) - 2):
                    idx0, idx1, idx2 = face[0], face[i + 1], face[i + 2]
                    
                    # Add triangle indices
                    indices.extend([idx0, idx1, idx2])
                    
                    # Calculate face normal
                    try:
                        v0 = vertex_array[idx0]
                        v1 = vertex_array[idx1]
                        v2 = vertex_array[idx2]
                        
                        edge1 = v1 - v0
                        edge2 = v2 - v0
                        normal = np.cross(edge1, edge2)
                        norm = np.linalg.norm(normal)
                        
                        if norm > 0:
                            normal = normal / norm
                            # Accumulate normals for smooth shading
                            normals_list[idx0] += normal
                            normals_list[idx1] += normal
                            normals_list[idx2] += normal
                    except (IndexError, ValueError):
                        continue
        
        # Normalize accumulated normals
        normal_array = np.zeros((len(vertices), 3), dtype=np.float32)
        for i, normal in enumerate(normals_list):
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal_array[i] = normal / norm
            else:
                normal_array[i] = [0, 0, 1]  # Default normal
        
        # Convert to contiguous arrays for OpenGL
        vertex_data = np.ascontiguousarray(vertex_array.flatten())
        normal_data = np.ascontiguousarray(normal_array.flatten())
        index_data = np.array(indices, dtype=np.uint32)
        
        return vertex_data, normal_data, index_data, len(index_data)
        
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        if self.last_pos:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            
            if event.buttons() & Qt.LeftButton:
                self.rotation_x += dy
                self.rotation_y += dx
                self.update()
            elif event.buttons() & Qt.RightButton:
                self.zoom += dy * 0.01
                self.update()
                
            self.last_pos = event.pos()
            
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom += delta * 0.001
        
        # Auto-LOD based on zoom level
        if self.auto_lod:
            self.update_auto_lod()
        
        self.update()
    
    def update_auto_lod(self):
        """Automatically adjust LOD based on zoom level"""
        if not self.lod_levels:
            return
            
        # Map zoom to LOD level (further away = lower LOD)
        if self.zoom > -2:  # Very close
            target_lod = 0
        elif self.zoom > -4:  # Close
            target_lod = 1
        elif self.zoom > -8:  # Medium distance
            target_lod = 2
        else:  # Far away
            target_lod = 3
            
        target_lod = min(target_lod, len(self.lod_levels) - 1)
        
        if target_lod != self.current_lod:
            self.current_lod = target_lod
            print(f"Auto-switched to LOD {self.current_lod}")
    
    def set_lod_level(self, level):
        """Manually set LOD level"""
        if 0 <= level < len(self.lod_levels):
            self.current_lod = level
            self.auto_lod = False
            self.update()
            print(f"Manually set to LOD {level}")
    
    def toggle_auto_lod(self):
        """Toggle automatic LOD adjustment"""
        self.auto_lod = not self.auto_lod
        if self.auto_lod:
            self.update_auto_lod()
        print(f"Auto-LOD: {'ON' if self.auto_lod else 'OFF'}")
    
    def load_all_objects(self, parser, file_path=None):
        """Load all objects from parser for multi-object view"""
        print("Loading all objects for multi-view...")
        
        # Try to load from cache if file_path is provided
        cache = get_cache()
        if file_path and cache.is_cached(file_path):
            cached_data = cache.load_cache(file_path)
            if cached_data:
                self.all_objects_data = cached_data['all_objects_data']
                print(f"✅ Loaded {len(self.all_objects_data)} objects from cache")
                return
        
        start_time = time.time()
        self.all_objects_data = {}
        
        # First, collect all vertices to find global center and scale
        all_vertices = []
        object_vertices = {}
        
        for obj_name in parser.objects.keys():
            vertices, faces = parser.get_object_vertices_for_display(obj_name)
            if not vertices or not faces:
                continue
            object_vertices[obj_name] = (vertices, faces)
            all_vertices.extend(vertices)
        
        if not all_vertices:
            print("No objects to load")
            return
        
        # Calculate global center and scale
        all_verts = np.array(all_vertices)
        global_center = np.mean(all_verts, axis=0)
        max_dim = np.max(np.abs(all_verts - global_center))
        
        # Generate random colors for each object
        import random
        random.seed(42)  # Consistent colors
        
        # Now process each object with global transform
        for obj_name, (vertices, faces) in object_vertices.items():
            # Apply global centering and scaling
            verts = np.array(vertices)
            centered_verts = verts - global_center
            if max_dim > 0:
                scaled_verts = (centered_verts / max_dim * 2).tolist()
            else:
                scaled_verts = centered_verts.tolist()
            
            # Generate LOD levels
            lod_levels = MeshSimplifier.create_lod_levels(scaled_verts, faces)
            
            # Create GPU buffers
            vbo_data_list = []
            for verts, lod_faces in lod_levels:
                vertex_data, normal_data, index_data, index_count = self.create_gpu_buffers(verts, lod_faces)
                vbo_data_list.append((vertex_data, normal_data, index_data, index_count))
            
            # Assign random color
            color = (random.uniform(0.4, 0.9), random.uniform(0.4, 0.9), random.uniform(0.4, 0.9))
            
            self.all_objects_data[obj_name] = (vbo_data_list, color, False)
            print(f"  Loaded {obj_name}: {len(vertices)} vertices, {len(faces)} faces")
        
        processing_time = time.time() - start_time
        print(f"Loaded {len(self.all_objects_data)} objects with global transform in {processing_time:.2f}s")
        
        # Save to cache if file_path is provided
        if file_path:
            cache_data = {
                'all_objects_data': self.all_objects_data
            }
            cache.save_cache(file_path, cache_data, processing_time)
    
    def toggle_object_selection(self, obj_name):
        """Toggle selection state of an object"""
        if obj_name in self.selected_objects:
            self.selected_objects.remove(obj_name)
        else:
            self.selected_objects.add(obj_name)
        self.update()
    
    def set_show_all_objects(self, show):
        """Toggle between single object and all objects view"""
        self.show_all_objects = show
        self.update()


class OBJParser:
    """Parser for OBJ 3D model files"""
    
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.objects = {}
        self.current_object = "default"
        self.materials = []
        self.normals = []
        self.texture_coords = []
        
    def parse_file(self, file_path):
        """Parse OBJ file and extract data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split()
                    if not parts:
                        continue
                        
                    command = parts[0]
                    
                    if command == 'v':  # Vertex
                        if len(parts) >= 4:
                            self.vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                    elif command == 'vn':  # Vertex normal
                        if len(parts) >= 4:
                            self.normals.append((float(parts[1]), float(parts[2]), float(parts[3])))
                    elif command == 'vt':  # Texture coordinate
                        if len(parts) >= 3:
                            self.texture_coords.append((float(parts[1]), float(parts[2])))
                    elif command == 'f':  # Face
                        face_data = parts[1:]
                        self.faces.append(face_data)
                        if self.current_object not in self.objects:
                            self.objects[self.current_object] = []
                        self.objects[self.current_object].append(face_data)
                    elif command == 'o' or command == 'g':  # Object or Group
                        if len(parts) > 1:
                            self.current_object = parts[1]
                        else:
                            self.current_object = f"object_{len(self.objects)}"
                    elif command == 'usemtl':  # Material
                        self.materials.append(parts[1])
                        
            return True
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False
    
    def get_statistics(self):
        """Get file statistics"""
        stats = {
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'objects': len(self.objects),
            'normals': len(self.normals),
            'texture_coords': len(self.texture_coords),
            'materials': len(set(self.materials))
        }
        return stats
    
    def split_objects(self):
        """Split objects into separate data structures"""
        split_data = {}
        
        for obj_name, obj_faces in self.objects.items():
            # Find all vertices used by this object
            used_vertices = set()
            used_normals = set()
            used_tex_coords = set()
            
            for face in obj_faces:
                for vertex_data in face:
                    # Parse vertex data (v/vt/vn format)
                    parts = vertex_data.split('/')
                    if parts[0]:  # Vertex index
                        used_vertices.add(int(parts[0]) - 1)  # OBJ indices are 1-based
                    if len(parts) > 1 and parts[1]:  # Texture coordinate
                        used_tex_coords.add(int(parts[1]) - 1)
                    if len(parts) > 2 and parts[2]:  # Normal
                        used_normals.add(int(parts[2]) - 1)
            
            # Create remapped indices
            vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_vertices))}
            normal_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_normals))}
            tex_coord_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_tex_coords))}
            
            # Remap faces
            remapped_faces = []
            for face in obj_faces:
                remapped_face = []
                for vertex_data in face:
                    parts = vertex_data.split('/')
                    new_data = []
                    
                    if parts[0]:  # Vertex
                        new_data.append(str(vertex_map[int(parts[0]) - 1] + 1))
                    else:
                        new_data.append('')
                    
                    if len(parts) > 1:
                        if parts[1]:  # Texture coordinate
                            new_data.append(str(tex_coord_map[int(parts[1]) - 1] + 1))
                        else:
                            new_data.append('')
                    else:
                        new_data.append('')
                    
                    if len(parts) > 2:
                        if parts[2]:  # Normal
                            new_data.append(str(normal_map[int(parts[2]) - 1] + 1))
                        else:
                            new_data.append('')
                    else:
                        new_data.append('')
                    
                    remapped_face.append('/'.join(new_data))
                remapped_faces.append(remapped_face)
            
            split_data[obj_name] = {
                'vertices': [self.vertices[i] for i in sorted(used_vertices)],
                'faces': remapped_faces,
                'normals': [self.normals[i] for i in sorted(used_normals)] if used_normals else [],
                'texture_coords': [self.texture_coords[i] for i in sorted(used_tex_coords)] if used_tex_coords else [],
                'vertex_indices': sorted(used_vertices)
            }
        
        return split_data
    
    def get_object_vertices_for_display(self, obj_name):
        """Get vertices and faces for OpenGL display"""
        if obj_name not in self.objects:
            return [], []
            
        obj_faces = self.objects[obj_name]
        used_vertices = set()
        
        for face in obj_faces:
            for vertex_data in face:
                parts = vertex_data.split('/')
                if parts[0]:
                    used_vertices.add(int(parts[0]) - 1)
        
        # Create vertex map
        vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_vertices))}
        vertices = [self.vertices[i] for i in sorted(used_vertices)]
        
        # Convert faces to index lists
        faces = []
        for face in obj_faces:
            face_indices = []
            for vertex_data in face:
                parts = vertex_data.split('/')
                if parts[0]:
                    old_idx = int(parts[0]) - 1
                    face_indices.append(vertex_map[old_idx])
            if len(face_indices) >= 3:
                faces.append(face_indices)
                
        return vertices, faces


class OBJProcessorApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.parser = OBJParser()
        self.current_file = None
        self.split_data = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('OBJ Model Processor with 3D Viewer')
        self.setGeometry(100, 100, 1600, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # File selection section
        file_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        self.file_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.browse_button = QPushButton('Browse OBJ File')
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel('File:'))
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - File info and objects list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File statistics
        self.stats_group = QGroupBox('File Statistics')
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel('Load an OBJ file to view statistics')
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        self.stats_group.setLayout(stats_layout)
        left_layout.addWidget(self.stats_group)
        
        # Objects list with checkboxes
        self.objects_group = QGroupBox('Objects in File (Click=View | Check=Highlight/Export)')
        objects_layout = QVBoxLayout()
        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.on_object_clicked)
        self.objects_list.itemChanged.connect(self.on_object_checkbox_changed)
        objects_layout.addWidget(self.objects_list)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        self.select_all_button = QPushButton('Select All')
        self.select_all_button.clicked.connect(self.select_all_objects)
        self.select_none_button = QPushButton('Select None')
        self.select_none_button.clicked.connect(self.select_no_objects)
        selection_layout.addWidget(self.select_all_button)
        selection_layout.addWidget(self.select_none_button)
        objects_layout.addLayout(selection_layout)
        
        self.objects_group.setLayout(objects_layout)
        left_layout.addWidget(self.objects_group)
        
        # Ground placement checkbox
        self.ground_checkbox = QCheckBox('Place on ground (Z=0) when exporting')
        self.ground_checkbox.setChecked(True)
        left_layout.addWidget(self.ground_checkbox)
        
        # Export button
        self.export_button = QPushButton('Export Selected as Printable OBJ')
        self.export_button.clicked.connect(self.export_selected_objects)
        self.export_button.setEnabled(False)
        left_layout.addWidget(self.export_button)
        
        splitter.addWidget(left_panel)
        
        # Middle panel - 3D Viewer
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        self.viewer_group = QGroupBox('3D Viewer')
        viewer_layout = QVBoxLayout()
        
        self.viewer = OBJViewer()
        viewer_layout.addWidget(self.viewer)
        
        # Viewer controls
        viewer_controls = QHBoxLayout()
        
        # View mode toggle
        self.show_all_checkbox = QCheckBox('Show All Objects')
        self.show_all_checkbox.stateChanged.connect(self.toggle_show_all)
        viewer_controls.addWidget(self.show_all_checkbox)
        
        viewer_controls.addWidget(QLabel('Left-drag: Rotate | Right-drag/Scroll: Zoom'))
        viewer_controls.addStretch()
        
        self.reset_view_button = QPushButton('Reset View')
        self.reset_view_button.clicked.connect(self.reset_viewer)
        viewer_controls.addWidget(self.reset_view_button)
        viewer_layout.addLayout(viewer_controls)
        
        # LOD controls
        lod_controls = QHBoxLayout()
        
        # Auto-LOD checkbox
        self.auto_lod_checkbox = QCheckBox('Auto LOD')
        self.auto_lod_checkbox.setChecked(True)
        self.auto_lod_checkbox.stateChanged.connect(self.toggle_auto_lod)
        lod_controls.addWidget(self.auto_lod_checkbox)
        
        # LOD slider
        lod_controls.addWidget(QLabel('Quality:'))
        self.lod_slider = QSlider(Qt.Horizontal)
        self.lod_slider.setMinimum(0)
        self.lod_slider.setMaximum(3)
        self.lod_slider.setValue(0)
        self.lod_slider.setTickPosition(QSlider.TicksBelow)
        self.lod_slider.setTickInterval(1)
        self.lod_slider.valueChanged.connect(self.on_lod_slider_changed)
        lod_controls.addWidget(self.lod_slider)
        
        # LOD labels
        lod_controls.addWidget(QLabel('High'))
        lod_controls.addStretch()
        lod_controls.addWidget(QLabel('Low'))
        
        viewer_layout.addLayout(lod_controls)
        
        self.viewer_group.setLayout(viewer_layout)
        middle_layout.addWidget(self.viewer_group)
        
        splitter.addWidget(middle_panel)
        
        # Right panel - Details display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Object details
        self.details_group = QGroupBox('Object Details')
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont('Courier', 9))
        details_layout.addWidget(self.details_text)
        self.details_group.setLayout(details_layout)
        right_layout.addWidget(self.details_group)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([350, 700, 550])
        main_layout.addWidget(splitter)
        
        # Menu bar
        menubar = self.menuBar()
        
        # Cache menu
        cache_menu = menubar.addMenu('Cache')
        
        cache_stats_action = cache_menu.addAction('Show Cache Stats')
        cache_stats_action.triggered.connect(self.show_cache_stats)
        
        clear_cache_action = cache_menu.addAction('Clear All Cache')
        clear_cache_action.triggered.connect(self.clear_all_cache)
        
        cleanup_cache_action = cache_menu.addAction('Cleanup Old Cache')
        cleanup_cache_action.triggered.connect(self.cleanup_cache)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
    def browse_file(self):
        """Browse for OBJ file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select OBJ File', '', 'OBJ Files (*.obj);;All Files (*)'
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load and parse OBJ file"""
        self.current_file = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.statusBar().showMessage('Loading file...')
        
        # Reset parser
        self.parser = OBJParser()
        
        # Reset viewer state
        self.viewer.all_objects_data = {}
        self.viewer.selected_objects.clear()
        self.viewer.show_all_objects = False
        self.viewer.vbo_data = []
        self.viewer.vertices = []
        self.viewer.faces = []
        
        # Reset UI state
        self.show_all_checkbox.setChecked(False)
        self.objects_list.clear()
        self.details_text.clear()
        self.stats_label.setText('Load an OBJ file to view statistics')
        
        # Update viewer to clear display
        self.viewer.update()
        
        # Parse file
        if self.parser.parse_file(file_path):
            self.display_file_info()
            self.export_button.setEnabled(True)
            self.statusBar().showMessage('File loaded successfully')
        else:
            QMessageBox.critical(self, 'Error', 'Failed to parse OBJ file')
            self.statusBar().showMessage('Error loading file')
    
    def display_file_info(self):
        """Display file statistics and objects"""
        stats = self.parser.get_statistics()
        
        # Update statistics
        stats_text = f"""Vertices: {stats['vertices']:,}
Faces: {stats['faces']:,}
Objects: {stats['objects']}
Normals: {stats['normals']:,}
Texture Coordinates: {stats['texture_coords']:,}
Materials: {stats['materials']}"""
        
        self.stats_label.setText(stats_text)
        
        # Update objects list with checkboxes
        self.objects_list.clear()
        for obj_name, obj_faces in self.parser.objects.items():
            item = QListWidgetItem(f"{obj_name} ({len(obj_faces)} faces)")
            item.setData(Qt.UserRole, obj_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.objects_list.addItem(item)
        
        self.export_button.setEnabled(True)
    
    def on_object_clicked(self, item):
        """Handle object click (text click) - show details"""
        obj_name = item.data(Qt.UserRole)
        obj_faces = self.parser.objects.get(obj_name, [])
        
        # In show-all mode, clicking text just shows details (no selection change)
        # In single-object mode, clicking shows the object in 3D viewer
        
        # Calculate object-specific statistics
        used_vertices = set()
        for face in obj_faces:
            for vertex_data in face:
                parts = vertex_data.split('/')
                if parts[0]:
                    used_vertices.add(int(parts[0]) - 1)
        
        # Get bounds
        if used_vertices:
            verts = np.array([self.parser.vertices[i] for i in used_vertices])
            min_bounds = np.min(verts, axis=0)
            max_bounds = np.max(verts, axis=0)
            size = max_bounds - min_bounds
            
            details = f"""Object: {obj_name}
Faces: {len(obj_faces)}
Vertices: {len(used_vertices)}

Bounding Box:
  Min: [{min_bounds[0]:.3f}, {min_bounds[1]:.3f}, {min_bounds[2]:.3f}]
  Max: [{max_bounds[0]:.3f}, {max_bounds[1]:.3f}, {max_bounds[2]:.3f}]
  Size: [{size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f}]

First 10 faces:
"""
        else:
            details = f"""Object: {obj_name}
Faces: {len(obj_faces)}
Vertices: 0

First 10 faces:
"""
            
        for i, face in enumerate(obj_faces[:10]):
            details += f"  {i+1}: {' '.join(face)}\n"
        
        if len(obj_faces) > 10:
            details += f"... and {len(obj_faces) - 10} more faces\n"
        
        self.details_text.setText(details)
        
        # Update 3D viewer only in single-object mode
        if not self.show_all_checkbox.isChecked():
            vertices, faces = self.parser.get_object_vertices_for_display(obj_name)
            self.viewer.set_model(vertices, faces)
            self.statusBar().showMessage(f'Viewing: {obj_name}')
    
    def on_object_checkbox_changed(self, item):
        """Handle checkbox state change - toggle highlight in all-objects view"""
        if not self.show_all_checkbox.isChecked():
            # In single-object mode, checkboxes are only for export selection
            return
        
        obj_name = item.data(Qt.UserRole)
        
        # Update viewer selection based on checkbox state
        if item.checkState() == Qt.Checked:
            if obj_name not in self.viewer.selected_objects:
                self.viewer.selected_objects.add(obj_name)
                self.viewer.update()
        else:
            if obj_name in self.viewer.selected_objects:
                self.viewer.selected_objects.remove(obj_name)
                self.viewer.update()
    
    def select_all_objects(self):
        """Select all objects"""
        for i in range(self.objects_list.count()):
            item = self.objects_list.item(i)
            item.setCheckState(Qt.Checked)
    
    def select_no_objects(self):
        """Deselect all objects"""
        for i in range(self.objects_list.count()):
            item = self.objects_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def reset_viewer(self):
        """Reset viewer to default position"""
        self.viewer.rotation_x = 0
        self.viewer.rotation_y = 0
        self.viewer.zoom = -5.0
        self.viewer.current_lod = 0
        self.lod_slider.setValue(0)
        self.viewer.update()
    
    def on_lod_slider_changed(self, value):
        """Handle LOD slider change"""
        self.viewer.set_lod_level(value)
    
    def toggle_auto_lod(self, state):
        """Toggle auto-LOD"""
        self.viewer.toggle_auto_lod()
        # Enable/disable slider based on auto-LOD state
        self.lod_slider.setEnabled(not self.viewer.auto_lod)
        if self.viewer.auto_lod:
            self.viewer.update_auto_lod()
    
    def toggle_show_all(self, state):
        """Toggle between single object and all objects view"""
        show_all = (state == Qt.Checked)
        self.viewer.set_show_all_objects(show_all)
        
        if show_all:
            # Load all objects if not already loaded
            if not self.viewer.all_objects_data:
                self.viewer.load_all_objects(self.parser, self.current_file)
            
            # Sync checkbox states with viewer selection
            for i in range(self.objects_list.count()):
                item = self.objects_list.item(i)
                obj_name = item.data(Qt.UserRole)
                if obj_name in self.viewer.selected_objects:
                    item.setCheckState(Qt.Checked)
            
            self.statusBar().showMessage('Showing all objects - Check boxes to highlight')
        else:
            self.statusBar().showMessage('Single object view')
    
    def export_selected_objects(self):
        """Export selected objects as printable OBJ files"""
        # Get selected objects
        selected_objects = []
        for i in range(self.objects_list.count()):
            item = self.objects_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_objects.append(item.data(Qt.UserRole))
        
        if not selected_objects:
            QMessageBox.warning(self, 'No Selection', 'Please select at least one object to export.')
            return
        
        # Ask for save location
        default_name = 'printable.obj' if len(selected_objects) == 1 else 'combined_printable.obj'
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Printable OBJ', default_name, 'OBJ Files (*.obj)'
        )
        
        if not filepath:
            return
        
        try:
            self.export_printable_obj(selected_objects, filepath)
            QMessageBox.information(self, 'Export Complete', 
                f'Exported {len(selected_objects)} object(s) to:\n{filepath}\n\nThe file is ready for 3D printing.')
            self.statusBar().showMessage(f'Exported printable OBJ: {os.path.basename(filepath)}')
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to export: {str(e)}')
    
    def export_printable_obj(self, object_names, output_path):
        """Export objects as a printable OBJ file with correct format and ground placement"""
        # Collect all faces and vertices from selected objects
        all_faces = []
        used_vertices = set()
        used_normals = set()
        used_tex_coords = set()
        
        for obj_name in object_names:
            if obj_name in self.parser.objects:
                obj_faces = self.parser.objects[obj_name]
                all_faces.extend(obj_faces)
                
                for face in obj_faces:
                    for vertex_data in face:
                        parts = vertex_data.split('/')
                        if parts[0]:
                            used_vertices.add(int(parts[0]) - 1)
                        if len(parts) > 1 and parts[1]:
                            used_tex_coords.add(int(parts[1]) - 1)
                        if len(parts) > 2 and parts[2]:
                            used_normals.add(int(parts[2]) - 1)
        
        # Get vertices
        vertices = np.array([self.parser.vertices[i] for i in sorted(used_vertices)])
        
        # Apply ground placement if requested
        if self.ground_checkbox.isChecked():
            min_z = np.min(vertices[:, 2])
            center_x = np.mean(vertices[:, 0])
            center_y = np.mean(vertices[:, 1])
            vertices[:, 0] -= center_x
            vertices[:, 1] -= center_y
            vertices[:, 2] -= min_z
        
        # Create remapping
        vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_vertices))}
        normal_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_normals))}
        tex_coord_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(used_tex_coords))}
        
        # Remap faces
        remapped_faces = []
        for face in all_faces:
            remapped_face = []
            for vertex_data in face:
                parts = vertex_data.split('/')
                new_data = []
                
                if parts[0]:
                    new_data.append(str(vertex_map[int(parts[0]) - 1] + 1))
                else:
                    new_data.append('')
                
                if len(parts) > 1:
                    if parts[1]:
                        new_data.append(str(tex_coord_map[int(parts[1]) - 1] + 1))
                    else:
                        new_data.append('')
                else:
                    new_data.append('')
                
                if len(parts) > 2:
                    if parts[2]:
                        new_data.append(str(normal_map[int(parts[2]) - 1] + 1))
                    else:
                        new_data.append('')
                else:
                    new_data.append('')
                
                remapped_face.append('/'.join(new_data))
            remapped_faces.append(remapped_face)
        
        # Write file with printable format
        has_normals = len(used_normals) > 0
        has_texcoords = len(used_tex_coords) > 0
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Printable OBJ exported from: {self.current_file}\n")
            f.write(f"# Objects: {', '.join(object_names)}\n")
            f.write(f"# Vertices: {len(vertices)}\n")
            f.write(f"# Faces: {len(remapped_faces)}\n")
            if self.ground_checkbox.isChecked():
                f.write(f"# Positioned on ground plane (Z=0) and centered at origin\n")
            f.write("\n")
            
            # Write vertices
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            # Write texture coordinates if any
            if has_texcoords:
                f.write("\n")
                for i in sorted(used_tex_coords):
                    vt = self.parser.texture_coords[i]
                    f.write(f"vt {vt[0]:.6f} {vt[1]:.6f}\n")
            
            # Write normals if any
            if has_normals:
                f.write("\n")
                for i in sorted(used_normals):
                    vn = self.parser.normals[i]
                    f.write(f"vn {vn[0]:.6f} {vn[1]:.6f} {vn[2]:.6f}\n")
            
            # Write faces with correct format
            f.write("\n")
            f.write(f"o PrintableObject\n")
            
            for face in remapped_faces:
                # Clean face format based on available data
                clean_face = []
                for vertex_data in face:
                    parts = vertex_data.split('/')
                    if parts[0]:
                        if not has_texcoords and not has_normals:
                            # Simple vertex-only format
                            clean_face.append(parts[0])
                        elif has_texcoords and not has_normals:
                            # vertex/texture format
                            if len(parts) > 1 and parts[1]:
                                clean_face.append(f"{parts[0]}/{parts[1]}")
                            else:
                                clean_face.append(parts[0])
                        elif not has_texcoords and has_normals:
                            # vertex//normal format
                            if len(parts) > 2 and parts[2]:
                                clean_face.append(f"{parts[0]}//{parts[2]}")
                            else:
                                clean_face.append(parts[0])
                        else:
                            # Full format
                            clean_face.append(vertex_data)
                
                if len(clean_face) >= 3:
                    f.write(f"f {' '.join(clean_face)}\n")
        
        QMessageBox.information(self, 'Export Complete', f'Exported to:\n{output_path}')
        self.statusBar().showMessage(f'Exported to: {output_path}')
    
    def show_cache_stats(self):
        """Show cache statistics"""
        cache = get_cache()
        stats = cache.get_cache_stats()
        
        msg = f"""Cache Statistics:

Total Files Cached: {stats['total_files']}
Total Cache Size: {stats['total_size_mb']:.2f} MB
Cache Directory: {stats['cache_dir']}

Cache entries are automatically cleaned up after 30 days of inactivity.
Maximum cache size is limited to 1 GB."""
        
        QMessageBox.information(self, 'Cache Statistics', msg)
    
    def clear_all_cache(self):
        """Clear all cache"""
        reply = QMessageBox.question(
            self, 'Clear Cache',
            'Are you sure you want to clear all cached data?\nThis will require reprocessing models on next load.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cache = get_cache()
            cache.clear_cache()
            QMessageBox.information(self, 'Cache Cleared', 'All cache has been cleared.')
    
    def cleanup_cache(self):
        """Cleanup old cache entries"""
        cache = get_cache()
        removed = cache.cleanup_old_cache(max_age_days=30, max_size_mb=1000)
        
        if removed > 0:
            QMessageBox.information(
                self, 'Cache Cleanup',
                f'Cleaned up {removed} old cache entries.'
            )
        else:
            QMessageBox.information(
                self, 'Cache Cleanup',
                'No old cache entries to clean up.'
            )


def main():
    app = QApplication(sys.argv)
    window = OBJProcessorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
