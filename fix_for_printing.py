import sys
import os
import numpy as np
from obj_model_processor import OBJParser

def analyze_object_bounds(obj_file_path):
    """Analyze the bounding box of an OBJ file"""
    parser = OBJParser()
    parser.parse_file(obj_file_path)
    
    if not parser.vertices:
        return None
    
    vertices = np.array(parser.vertices)
    
    min_bounds = np.min(vertices, axis=0)
    max_bounds = np.max(vertices, axis=0)
    center = (min_bounds + max_bounds) / 2
    
    return {
        'min_bounds': min_bounds,
        'max_bounds': max_bounds,
        'center': center,
        'size': max_bounds - min_bounds,
        'vertex_count': len(vertices)
    }

def recenter_to_ground(obj_file_path, output_path):
    """Recenter object so it sits on the ground plane (Z=0) and is centered at origin"""
    
    parser = OBJParser()
    parser.parse_file(obj_file_path)
    
    if not parser.vertices:
        print("No vertices found in file")
        return False
    
    vertices = np.array(parser.vertices)
    
    # Find minimum Z value (lowest point)
    min_z = np.min(vertices[:, 2])
    
    # Calculate center in X and Y (for centering)
    center_x = np.mean(vertices[:, 0])
    center_y = np.mean(vertices[:, 1])
    
    # Apply transformation: center X,Y and move Z so lowest point is at 0
    transformed_vertices = []
    for v in vertices:
        new_v = (
            v[0] - center_x,  # Center X
            v[1] - center_y,  # Center Y
            v[2] - min_z      # Move to ground
        )
        transformed_vertices.append(new_v)
    
    # Write the corrected OBJ file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Fixed for 3D printing from: {obj_file_path}\n")
        f.write(f"# Recentered to ground and centered at origin\n")
        f.write(f"# Original vertices: {len(transformed_vertices)}\n\n")
        
        # Write transformed vertices
        for v in transformed_vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        # Write texture coordinates if any
        if parser.texture_coords:
            f.write("\n")
            for vt in parser.texture_coords:
                f.write(f"vt {vt[0]:.6f} {vt[1]:.6f}\n")
        
        # Write normals if any
        if parser.normals:
            f.write("\n")
            for vn in parser.normals:
                f.write(f"vn {vn[0]:.6f} {vn[1]:.6f} {vn[2]:.6f}\n")
        
        # Write faces (no need to remap since we kept all vertices)
        f.write("\n")
        f.write("o FixedObject\n")
        for face in parser.faces:
            f.write(f"f {' '.join(face)}\n")
    
    print(f"Fixed object saved to: {output_path}")
    print(f"  Translation: X={-center_x:.3f}, Y={-center_y:.3f}, Z={-min_z:.3f}")
    return True

def fix_obj_for_printing(obj_file_path, output_path=None):
    """Fix common OBJ issues for 3D printing software compatibility"""
    
    if output_path is None:
        base_name = os.path.splitext(obj_file_path)[0]
        output_path = f"{base_name}_fixed.obj"
    
    parser = OBJParser()
    parser.parse_file(obj_file_path)
    
    print(f"Processing: {obj_file_path}")
    print(f"Original vertices: {len(parser.vertices)}")
    print(f"Original faces: {len(parser.faces)}")
    
    # First, recenter to ground
    temp_path = output_path.replace('.obj', '_temp.obj')
    if recenter_to_ground(obj_file_path, temp_path):
        # Parse the recentered file
        temp_parser = OBJParser()
        temp_parser.parse_file(temp_path)
        
        # Additional fixes for 3D printing software
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 3D Printing Fixed OBJ from: {obj_file_path}\n")
            f.write(f"# Recentered to ground, centered at origin\n")
            f.write(f"# Vertices: {len(temp_parser.vertices)}\n")
            f.write(f"# Faces: {len(temp_parser.faces)}\n\n")
            
            # Write vertices with consistent formatting
            vertex_count = 0
            for v in temp_parser.vertices:
                vertex_count += 1
                # Ensure consistent decimal places and no scientific notation
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            # Write texture coordinates if any
            if temp_parser.texture_coords:
                f.write("\n")
                for vt in temp_parser.texture_coords:
                    f.write(f"vt {vt[0]:.6f} {vt[1]:.6f}\n")
            
            # Write normals if any
            if temp_parser.normals:
                f.write("\n")
                for vn in temp_parser.normals:
                    f.write(f"vn {vn[0]:.6f} {vn[1]:.6f} {vn[2]:.6f}\n")
            
            # Write faces with validation
            f.write("\n")
            f.write("o PrintableObject\n")
            face_count = 0
            has_normals = len(temp_parser.normals) > 0
            has_texcoords = len(temp_parser.texture_coords) > 0
            
            for face in temp_parser.faces:
                face_count += 1
                # Validate face indices
                valid_face = []
                for vertex_data in face:
                    parts = vertex_data.split('/')
                    if parts[0]:  # Vertex index
                        try:
                            vertex_idx = int(parts[0])
                            if 1 <= vertex_idx <= len(temp_parser.vertices):
                                # Clean up face format based on available data
                                if not has_texcoords and not has_normals:
                                    # Simple vertex-only format
                                    valid_face.append(parts[0])
                                elif has_texcoords and not has_normals:
                                    # vertex/texture format
                                    if len(parts) > 1 and parts[1]:
                                        valid_face.append(f"{parts[0]}/{parts[1]}")
                                    else:
                                        valid_face.append(parts[0])
                                elif not has_texcoords and has_normals:
                                    # vertex//normal format
                                    if len(parts) > 2 and parts[2]:
                                        valid_face.append(f"{parts[0]}//{parts[2]}")
                                    else:
                                        valid_face.append(parts[0])
                                else:
                                    # vertex/texture/normal format
                                    valid_face.append(vertex_data)
                        except ValueError:
                            continue
                
                if len(valid_face) >= 3:  # Only write valid faces
                    f.write(f"f {' '.join(valid_face)}\n")
            
            print(f"Final fixed file: {output_path}")
            print(f"  Valid faces written: {face_count}")
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return True
    
    return False

def analyze_and_fix_split_objects(split_dir):
    """Analyze and fix both split objects for 3D printing"""
    
    object1_path = os.path.join(split_dir, "Object1.obj")
    object2_path = os.path.join(split_dir, "Object2.obj")
    
    if not os.path.exists(object1_path) or not os.path.exists(object2_path):
        print("Split objects not found. Run object_grouper.py first.")
        return
    
    print("Analyzing split objects...")
    print("=" * 50)
    
    # Analyze original objects
    obj1_analysis = analyze_object_bounds(object1_path)
    obj2_analysis = analyze_object_bounds(object2_path)
    
    if obj1_analysis and obj2_analysis:
        print("Object1 bounds:")
        print(f"  Min: [{obj1_analysis['min_bounds'][0]:.2f}, {obj1_analysis['min_bounds'][1]:.2f}, {obj1_analysis['min_bounds'][2]:.2f}]")
        print(f"  Max: [{obj1_analysis['max_bounds'][0]:.2f}, {obj1_analysis['max_bounds'][1]:.2f}, {obj1_analysis['max_bounds'][2]:.2f}]")
        print(f"  Center: [{obj1_analysis['center'][0]:.2f}, {obj1_analysis['center'][1]:.2f}, {obj1_analysis['center'][2]:.2f}]")
        print(f"  Size: [{obj1_analysis['size'][0]:.2f}, {obj1_analysis['size'][1]:.2f}, {obj1_analysis['size'][2]:.2f}]")
        
        print("\nObject2 bounds:")
        print(f"  Min: [{obj2_analysis['min_bounds'][0]:.2f}, {obj2_analysis['min_bounds'][1]:.2f}, {obj2_analysis['min_bounds'][2]:.2f}]")
        print(f"  Max: [{obj2_analysis['max_bounds'][0]:.2f}, {obj2_analysis['max_bounds'][1]:.2f}, {obj2_analysis['max_bounds'][2]:.2f}]")
        print(f"  Center: [{obj2_analysis['center'][0]:.2f}, {obj2_analysis['center'][1]:.2f}, {obj2_analysis['center'][2]:.2f}]")
        print(f"  Size: [{obj2_analysis['size'][0]:.2f}, {obj2_analysis['size'][1]:.2f}, {obj2_analysis['size'][2]:.2f}]")
        
        # Determine which object is on top (higher Z values)
        obj1_max_z = obj1_analysis['max_bounds'][2]
        obj2_max_z = obj2_analysis['max_bounds'][2]
        
        print(f"\nZ-position analysis:")
        print(f"  Object1 max Z: {obj1_max_z:.2f}")
        print(f"  Object2 max Z: {obj2_max_z:.2f}")
        
        if obj1_max_z > obj2_max_z:
            print("  Object1 is positioned above Object2")
        else:
            print("  Object2 is positioned above Object1")
    
    print("\n" + "=" * 50)
    print("Fixing objects for 3D printing...")
    
    # Fix both objects
    obj1_fixed = fix_obj_for_printing(object1_path, os.path.join(split_dir, "Object1_printable.obj"))
    obj2_fixed = fix_obj_for_printing(object2_path, os.path.join(split_dir, "Object2_printable.obj"))
    
    if obj1_fixed and obj2_fixed:
        print("\n" + "=" * 50)
        print("Objects fixed successfully!")
        print("Fixed files:")
        print(f"  {os.path.join(split_dir, 'Object1_printable.obj')}")
        print(f"  {os.path.join(split_dir, 'Object2_printable.obj')}")
        print("\nThese files should now work with 3D printing software and each object sits on the ground plane.")

def main():
    if len(sys.argv) == 1:
        # No arguments - fix the split objects
        split_dir = "split_objects"
        if os.path.exists(split_dir):
            analyze_and_fix_split_objects(split_dir)
        else:
            print("split_objects directory not found. Run object_grouper.py first.")
    elif len(sys.argv) == 2:
        # Single OBJ file - fix it
        obj_file_path = sys.argv[1]
        if os.path.exists(obj_file_path):
            fix_obj_for_printing(obj_file_path)
        else:
            print(f"File not found: {obj_file_path}")
    else:
        print("Usage:")
        print("  python fix_for_printing.py                    # Fix split objects")
        print("  python fix_for_printing.py <obj_file_path>    # Fix single OBJ file")

if __name__ == "__main__":
    main()
