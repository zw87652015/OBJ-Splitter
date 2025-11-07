"""
Model Cache System for OBJ Processor
Caches preprocessed model data (LOD levels, GPU buffers) for faster loading
"""

import os
import json
import hashlib
import pickle
import time
from pathlib import Path


class ModelCache:
    """Manages caching of preprocessed OBJ model data"""
    
    def __init__(self, cache_dir=None):
        """Initialize cache system"""
        if cache_dir is None:
            # Use project directory for cache
            project_dir = Path(__file__).parent
            cache_dir = project_dir / ".cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self.load_index()
        
        print(f"Cache directory: {self.cache_dir}")
    
    def load_index(self):
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache index: {e}")
                return {}
        return {}
    
    def save_index(self):
        """Save cache index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache index: {e}")
    
    def compute_file_hash(self, file_path):
        """Compute SHA256 hash of file"""
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"Error computing hash: {e}")
            return None
    
    def get_cache_path(self, file_hash):
        """Get cache file path for a given hash"""
        return self.cache_dir / f"{file_hash}.cache"
    
    def is_cached(self, file_path):
        """Check if file is cached and cache is valid (by hash, not path)"""
        file_path = str(file_path)
        
        # Compute hash first
        file_hash = self.compute_file_hash(file_path)
        if file_hash is None:
            return False
        
        # Check if cache file exists for this hash
        cache_path = self.get_cache_path(file_hash)
        if not cache_path.exists():
            return False
        
        # Cache exists! Update index if this is a new path for same content
        if file_path not in self.cache_index:
            print(f"Cache hit: Same content as existing cache (copied/renamed file)")
            # Add this path to index pointing to same hash
            self.cache_index[file_path] = {
                'hash': file_hash,
                'original_name': os.path.basename(file_path),
                'cached_at': time.time(),
                'last_accessed': time.time(),
                'processing_time': 0,  # Unknown for reused cache
                'cache_size_mb': cache_path.stat().st_size / (1024 * 1024)
            }
            self.save_index()
        else:
            # Verify hash matches
            cache_entry = self.cache_index[file_path]
            if cache_entry['hash'] != file_hash:
                print(f"Cache invalid: File has been modified")
                return False
        
        return True
    
    def load_cache(self, file_path):
        """Load cached model data"""
        file_path = str(file_path)
        
        if not self.is_cached(file_path):
            return None
        
        # Get hash (either from index or compute it)
        if file_path in self.cache_index:
            file_hash = self.cache_index[file_path]['hash']
        else:
            file_hash = self.compute_file_hash(file_path)
        
        cache_path = self.get_cache_path(file_hash)
        
        try:
            cache_entry = self.cache_index.get(file_path, {})
            original_name = cache_entry.get('original_name', os.path.basename(file_path))
            processing_time = cache_entry.get('processing_time', 0)
            
            print(f"Loading from cache: {original_name}")
            start_time = time.time()
            
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            load_time = time.time() - start_time
            print(f"✅ Cache loaded in {load_time:.2f}s (saved {processing_time:.2f}s)")
            
            # Update access time
            if file_path in self.cache_index:
                self.cache_index[file_path]['last_accessed'] = time.time()
                self.save_index()
            
            return cached_data
            
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None
    
    def save_cache(self, file_path, model_data, processing_time=0):
        """Save model data to cache"""
        file_path = str(file_path)
        file_hash = self.compute_file_hash(file_path)
        
        if file_hash is None:
            print("Cannot cache: Failed to compute file hash")
            return False
        
        cache_path = self.get_cache_path(file_hash)
        
        # Check if cache already exists for this hash (duplicate content)
        if cache_path.exists():
            print(f"Cache already exists for this content (duplicate file)")
            # Just update index to include this path
            self.cache_index[file_path] = {
                'hash': file_hash,
                'original_name': os.path.basename(file_path),
                'cached_at': time.time(),
                'last_accessed': time.time(),
                'processing_time': processing_time,
                'cache_size_mb': cache_path.stat().st_size / (1024 * 1024)
            }
            self.save_index()
            return True
        
        try:
            print(f"Saving to cache...")
            start_time = time.time()
            
            with open(cache_path, 'wb') as f:
                pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            save_time = time.time() - start_time
            cache_size = cache_path.stat().st_size / (1024 * 1024)  # MB
            
            # Update index
            self.cache_index[file_path] = {
                'hash': file_hash,
                'original_name': os.path.basename(file_path),
                'cached_at': time.time(),
                'last_accessed': time.time(),
                'processing_time': processing_time,
                'cache_size_mb': cache_size
            }
            self.save_index()
            
            print(f"✅ Cache saved in {save_time:.2f}s ({cache_size:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def clear_cache(self, file_path=None):
        """Clear cache for specific file or all files"""
        if file_path:
            # Clear specific file path from index
            file_path = str(file_path)
            if file_path in self.cache_index:
                cache_entry = self.cache_index[file_path]
                file_hash = cache_entry['hash']
                
                # Remove this path from index
                del self.cache_index[file_path]
                
                # Check if any other paths reference this hash
                paths_with_hash = [path for path, entry in self.cache_index.items() 
                                  if entry['hash'] == file_hash]
                
                if not paths_with_hash:
                    # No other paths reference this hash, delete cache file
                    cache_path = self.get_cache_path(file_hash)
                    if cache_path.exists():
                        cache_path.unlink()
                        print(f"Cache file deleted (no longer referenced)")
                
                self.save_index()
                print(f"Cache cleared for: {os.path.basename(file_path)}")
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.cache_index = {}
            self.save_index()
            print("All cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total_size = 0
        total_files = len(self.cache_index)
        
        for entry in self.cache_index.values():
            total_size += entry.get('cache_size_mb', 0)
        
        return {
            'total_files': total_files,
            'total_size_mb': total_size,
            'cache_dir': str(self.cache_dir)
        }
    
    def cleanup_old_cache(self, max_age_days=30, max_size_mb=1000):
        """Remove old or excess cache entries"""
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache_index.items(),
            key=lambda x: x[1].get('last_accessed', 0)
        )
        
        total_size = 0
        to_remove = []
        
        for file_path, entry in sorted_entries:
            age = current_time - entry.get('last_accessed', 0)
            size = entry.get('cache_size_mb', 0)
            
            # Remove if too old
            if age > max_age_seconds:
                to_remove.append(file_path)
                continue
            
            # Remove if total size exceeds limit
            total_size += size
            if total_size > max_size_mb:
                to_remove.append(file_path)
        
        # Remove marked entries
        for file_path in to_remove:
            self.clear_cache(file_path)
        
        if to_remove:
            print(f"Cleaned up {len(to_remove)} old cache entries")
        
        return len(to_remove)


# Singleton instance
_cache_instance = None

def get_cache():
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ModelCache()
    return _cache_instance
