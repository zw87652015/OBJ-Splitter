import sys
import os
from obj_model_processor import OBJParser

def analyze_and_group_objects(obj_file_path):
    """Analyze OBJ file and suggest grouping for 2 main objects"""
    
    print(f"Analyzing: {obj_file_path}")
    print("=" * 50)
    
    # Parse the OBJ file
    parser = OBJParser()
    if not parser.parse_file(obj_file_path):
        print("Failed to parse OBJ file")
        return
    
    # Get statistics
    stats = parser.get_statistics()
    print(f"Total Statistics:")
    print(f"  Vertices: {stats['vertices']:,}")
    print(f"  Faces: {stats['faces']:,}")
    print(f"  Objects/Groups: {stats['objects']}")
    print()
    
    # Analyze objects and their face counts
    objects_info = []
    for obj_name, obj_faces in parser.objects.items():
        # Calculate unique vertices for this object
        used_vertices = set()
        for face in obj_faces:
            for vertex_data in face:
                parts = vertex_data.split('/')
                if parts[0]:
                    used_vertices.add(int(parts[0]) - 1)
        
        objects_info.append({
            'name': obj_name,
            'faces': len(obj_faces),
            'vertices': len(used_vertices)
        })
    
    # Sort by face count for easier grouping
    objects_info.sort(key=lambda x: x['faces'], reverse=True)
    
    print("Individual Objects:")
    for obj in objects_info:
        print(f"  {obj['name']}: {obj['faces']:,} faces, {obj['vertices']:,} vertices")
    print()
    
    # Group objects by face count (identical copies)
    face_count_groups = {}
    for obj in objects_info:
        face_count = obj['faces']
        if face_count not in face_count_groups:
            face_count_groups[face_count] = []
        face_count_groups[face_count].append(obj)
    
    print("Identified Groups (by face count):")
    group_id = 1
    suggested_groups = []
    
    for face_count, objects in face_count_groups.items():
        if len(objects) > 1:
            print(f"  Group {group_id} - {len(objects)} identical objects:")
            for obj in objects:
                print(f"    {obj['name']}")
            suggested_groups.append(objects)
            group_id += 1
    
    print()
    
    # Create 2 main object groupings
    if len(suggested_groups) >= 1:
        print("Suggested 2 Main Objects:")
        print("  Object 1: First copy of each group")
        print("  Object 2: Second copy of each group")
        print()
        
        # Create the two groupings
        object1_groups = []
        object2_groups = []
        
        for group in suggested_groups:
            if len(group) >= 2:
                object1_groups.append(group[0]['name'])
                object2_groups.append(group[1]['name'])
            elif len(group) == 1:
                # If only one copy, assign to object 1
                object1_groups.append(group[0]['name'])
        
        print("Object 1 Groups:")
        for group_name in object1_groups:
            print(f"  {group_name}")
        
        print("\nObject 2 Groups:")
        for group_name in object2_groups:
            print(f"  {group_name}")
        
        print()
        print("Total faces per main object:")
        
        # Calculate totals
        obj1_faces = sum(len(parser.objects[name]) for name in object1_groups)
        obj2_faces = sum(len(parser.objects[name]) for name in object2_groups)
        
        print(f"  Object 1: {obj1_faces:,} faces")
        print(f"  Object 2: {obj2_faces:,} faces")
        print(f"  Total: {obj1_faces + obj2_faces:,} faces (should match total)")
        
        return object1_groups, object2_groups
    
    return None, None

def export_grouped_objects(obj_file_path, object1_groups, object2_groups, output_dir):
    """Export the two main objects as separate OBJ files"""
    
    parser = OBJParser()
    parser.parse_file(obj_file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Export Object 1
    export_single_object(parser, object1_groups, obj_file_path, os.path.join(output_dir, "Object1.obj"), "Object1")
    
    # Export Object 2  
    export_single_object(parser, object2_groups, obj_file_path, os.path.join(output_dir, "Object2.obj"), "Object2")

def export_single_object(parser, group_names, obj_file_path, output_path, object_name):
    """Export a single object composed of multiple groups"""
    
    # Collect all faces from specified groups
    all_faces = []
    used_vertices = set()
    used_normals = set()
    used_tex_coords = set()
    
    for group_name in group_names:
        if group_name in parser.objects:
            group_faces = parser.objects[group_name]
            all_faces.extend(group_faces)
            
            # Find all vertices used by this group
            for face in group_faces:
                for vertex_data in face:
                    parts = vertex_data.split('/')
                    if parts[0]:  # Vertex index
                        used_vertices.add(int(parts[0]) - 1)
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
    for face in all_faces:
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
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Exported from: {obj_file_path}\n")
        f.write(f"# Main Object: {object_name}\n")
        f.write(f"# Groups: {', '.join(group_names)}\n")
        f.write(f"# Vertices: {len(sorted(used_vertices))}\n")
        f.write(f"# Faces: {len(remapped_faces)}\n\n")
        
        # Write vertices
        for i in sorted(used_vertices):
            v = parser.vertices[i]
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        # Write texture coordinates if any
        if used_tex_coords:
            f.write("\n")
            for i in sorted(used_tex_coords):
                vt = parser.texture_coords[i]
                f.write(f"vt {vt[0]:.6f} {vt[1]:.6f}\n")
        
        # Write normals if any
        if used_normals:
            f.write("\n")
            for i in sorted(used_normals):
                vn = parser.normals[i]
                f.write(f"vn {vn[0]:.6f} {vn[1]:.6f} {vn[2]:.6f}\n")
        
        # Write faces
        f.write("\n")
        f.write(f"o {object_name}\n")
        for face in remapped_faces:
            f.write(f"f {' '.join(face)}\n")
    
    print(f"Exported {object_name} to: {output_path}")
    print(f"  Groups: {', '.join(group_names)}")
    print(f"  Vertices: {len(sorted(used_vertices))}")
    print(f"  Faces: {len(remapped_faces)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python object_grouper.py <obj_file_path>")
        print("Example: python object_grouper.py Xingyun.obj")
        return
    
    obj_file_path = sys.argv[1]
    
    if not os.path.exists(obj_file_path):
        print(f"File not found: {obj_file_path}")
        return
    
    # Analyze and get groupings
    object1_groups, object2_groups = analyze_and_group_objects(obj_file_path)
    
    if object1_groups and object2_groups:
        print("\n" + "=" * 50)
        print("Do you want to export these 2 main objects? (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            output_dir = os.path.join(os.path.dirname(obj_file_path), "split_objects")
            export_grouped_objects(obj_file_path, object1_groups, object2_groups, output_dir)
            print(f"\nObjects exported to: {output_dir}")
        else:
            print("Export cancelled.")
    else:
        print("Could not identify clear grouping for 2 main objects.")

if __name__ == "__main__":
    main()
