# OBJ Model Processor with 3D Viewer

A PyQt6 application with Material Design 3 styling for analyzing, visualizing, and exporting OBJ 3D model files with GPU-accelerated rendering, intelligent caching, and 3D printing support.

## Features

- **3D Visualization**: Real-time OpenGL-based 3D viewer with interactive rotation and zoom
- **GPU Acceleration**: VBO-based rendering for smooth 60 FPS performance even with 500K+ faces
- **LOD System**: 4 levels of detail (100%, 50%, 25%, 10%) with automatic/manual control
- **Intelligent Caching**: 5-10x faster loading for previously opened files with SHA256 verification
- **Content-Based Cache**: Copied/renamed files automatically reuse existing cache
- **Multi-Object View**: Display all objects simultaneously with selection highlighting
- **File Analysis**: Parse and display detailed information about OBJ files including vertices, faces, objects, normals, and texture coordinates
- **Object Detection**: Automatically identify and list all objects/groups within an OBJ file
- **Multi-Object Selection**: Select multiple objects to combine and export as a single file
- **Printable Export**: Export with correct face format (fixes malformed `v//` format) for 3D printing software compatibility
- **Ground Placement**: Automatically center objects and place them on the ground plane (Z=0) for 3D printing
- **Interactive UI**: User-friendly interface with 3D viewer, resizable panels, and detailed object information

## Quick Start

### Installation (Windows)

**Option 1: Automatic Installation Script**
```bash
# Run the batch file
install.bat
```

**Option 2: Manual Installation**
```bash
# Install dependencies using Aliyun mirror (faster in China)
pip install PyQt6==6.10.0 numpy PyOpenGL==3.1.7 -i https://mirrors.aliyun.com/pypi/simple/

# Optional: Install PyOpenGL-accelerate for better performance
# Requires Microsoft Visual C++ Build Tools
pip install PyOpenGL-accelerate -i https://mirrors.aliyun.com/pypi/simple/
```

**Option 3: Python Installation Script**
```bash
python install.py
```

### Running the Application
```bash
python main.py
```

## Usage Guide

### Loading Files
1. Click **Browse** or drag-and-drop OBJ files
2. Select file from file dialog
3. View file statistics and object list
4. Objects appear in the list with checkboxes

### 3D Viewer Controls
- **Left Mouse**: Rotate model
- **Right Mouse**: Pan view
- **Mouse Wheel**: Zoom in/out
- **LOD Slider**: Adjust detail level (0=highest, 3=lowest)
- **Auto-LOD Checkbox**: Enable automatic LOD based on zoom distance

### View Modes
- **Single Object**: Click object name to view it alone
- **All Objects**: Check "Show All Objects" to see entire model
- **Selection**: In all-objects mode, check boxes to highlight with orange border

### Exporting
1. Select objects using checkboxes
2. Click **Export Selected**
3. Choose output location
4. Options:
   - **Place on Ground**: Center and set Z=0 for 3D printing
   - **Fix Face Format**: Ensure compatibility with 3D software

## Cache System

The application includes intelligent caching for instant loading of previously processed files:

### How It Works
- **Content-Based**: Cache is based on file content (SHA256 hash), not file name
- **Smart Reuse**: Copied or renamed files automatically use existing cache
- **Automatic Management**: No configuration needed

### Performance
- **First Load**: 300K faces in ~7.5s
- **Cached Load**: Same file in ~1.1s (7x faster)
- **Copied Files**: Instant loading from existing cache

### Cache Location
- **Directory**: `.cache/` (in project folder)
- **Git Ignored**: Won't be committed to version control
- **Management**: Menu → Cache (view stats, clear, cleanup)

### Example Behavior
```
model.obj → Load first time (7.5s) → Cache created
model_copy.obj → Load (0.3s) ✅ Reuses cache
renamed.obj → Load (0.3s) ✅ Reuses cache
```

## Technical Details

### GPU Acceleration
- **Vertex Buffer Objects (VBOs)**: Hardware-accelerated rendering
- **Index Buffer**: Efficient face rendering with `glDrawElements`
- **60 FPS**: Smooth performance with complex models

### LOD (Level of Detail) System
- **LOD 0**: 100% faces (highest quality)
- **LOD 1**: 50% faces (medium quality)
- **LOD 2**: 25% faces (low quality)
- **LOD 3**: 10% faces (lowest quality, fastest)

**Automatic LOD**: Based on zoom distance
- Zoom > -2: LOD 0
- Zoom > -4: LOD 1
- Zoom > -8: LOD 2
- Zoom ≤ -8: LOD 3

### Multi-Object View Features
- **Global Centering**: All objects positioned relative to overall center
- **Random Colors**: Each object gets unique color for easy identification
- **Selection Highlighting**: Orange border for selected objects
- **Dimming**: Unselected objects appear dimmed

### File Format Support
- **Input**: OBJ files with vertices, faces, normals, texture coordinates
- **Face Formats**: Handles v, v/t, v//n, v/t/n formats
- **Output**: Clean, printable OBJ format

## Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version (3.7+ required)
python --version

# Install dependencies
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**OpenGL errors**
- Update graphics drivers
- Try without PyOpenGL-accelerate (optional dependency)
- Ensure OpenGL 3.0+ support

**Slow performance**
- Enable LOD system: Check "Auto-LOD" or use LOD slider
- Use lower LOD for large models
- Enable GPU acceleration (automatic)

**Cache not working**
- Check `.cache/` directory exists and is writable
- Clear cache: Menu → Cache → Clear All Cache
- Ensure sufficient disk space

### Performance Tips

1. **Use LOD**: Enable Auto-LOD for automatic performance adjustment
2. **Cache Benefits**: Large files see 5-10x speedup after first load
3. **Multi-Object View**: More efficient than loading objects individually
4. **GPU Acceleration**: Automatic for better performance

## File Structure

```
ObjModelProcessor/
├── main.py                  # Main application
├── model_cache.py           # Caching system
├── fix_for_printing.py      # Export utilities
├── object_grouper.py        # Object grouping
├── requirements.txt         # Dependencies
├── install.py              # Installation script
├── install.bat             # Windows installation
├── .cache/                 # Cache directory (git ignored)
├── .gitignore              # Git ignore rules
├── Timeline.md             # Development history
└── README.md               # This file
```

## Development

### Dependencies
- **PyQt6**: Modern GUI framework with Material Design 3 support
- **PyOpenGL**: 3D rendering
- **NumPy**: Numerical computations

### Key Components
- **main.py**: Main application with PyQt6 GUI and Material Design 3 styling
- **md3_styles.py**: Material Design 3 color system and stylesheets
- **OBJViewer**: OpenGL 3D widget with GPU rendering
- **MeshSimplifier**: LOD generation algorithms
- **ModelCache**: Content-based caching system
- **OBJParser**: OBJ file parsing and processing

## Git Setup

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: OBJ Model Processor"

# Add remote
git remote add origin https://github.com/yourusername/ObjModelProcessor.git
git push -u origin main
```

The `.gitignore` excludes `.cache/` and other generated files.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify dependencies are installed correctly
3. Ensure graphics drivers support OpenGL 3.0+
4. Check Timeline.md for development history

---

**Note**: This project follows the "single README" rule. All documentation is consolidated here except for Timeline.md which tracks development history.
