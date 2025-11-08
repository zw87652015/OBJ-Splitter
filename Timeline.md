📜 Log Entry
- Date: 2025-11-08
- Type: design-discuss
- Module: docs/, README.md
- Summary: Consolidate docs to single README and add Timeline logs per project rules
- Reason: Project rule requires only one README and a Timeline; reduce fragmentation
- Alternatives: Keep multiple guides; move into docs/ directory; both rejected
- Risk/Follow-up: Ensure README includes all essential sections; keep Timeline updated
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: design-discuss
- Module: model_cache.py
- Summary: Switch cache key to content hash, enabling reuse for copied/renamed files
- Reason: Improve UX and performance; identical files should hit cache regardless of path
- Alternatives: Path-based cache; dual-key (path+hash); rejected
- Risk/Follow-up: Index can grow with many paths; consider LRU for index entries
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: refactor
- Module: obj_model_processor.py → main.py
- Summary: Rename main entry file from obj_model_processor.py to main.py
- Reason: Simplify entry point name; follow Python convention for main scripts
- Alternatives: Keep obj_model_processor.py; use app.py; rejected for simplicity
- Risk/Follow-up: Update documentation and run commands
- Breaking: yes (filename change)
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: ui-improve
- Module: main.py
- Summary: Fully adjustable splitter panels with persistent layout like commercial software
- Reason: Users should be able to resize functional partitions and have preferences remembered
- Alternatives: Fixed layout; tabs; implemented adjustable splitters with state persistence
- Risk/Follow-up: Ensure minimum widths prevent unusable layouts
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: perf-optimize
- Module: main.py
- Summary: Unified cache system storing both single-object and multi-object data in same cache file
- Reason: Single-object mode was recreating processed data already cached for multi-object mode
- Alternatives: Separate cache files; shared cache references; implemented unified cache structure
- Risk/Follow-up: Larger cache files but eliminates duplicate processing
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: ui-change
- Module: main.py
- Summary: Initialize application with "Show All Objects" mode enabled by default
- Reason: Users want to see the full model immediately upon loading, not individual objects
- Alternatives: Remember last mode; add setting; implemented default to full model view
- Risk/Follow-up: Ensure single-object mode still works when toggled
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: ui-improve
- Module: main.py
- Summary: Replace mode checkbox with toggle button showing current mode visually
- Reason: Checkbox doesn't clearly indicate which mode is active; button provides better visual feedback
- Alternatives: Radio buttons; segmented control; implemented styled toggle button
- Risk/Follow-up: Ensure button styling works across different themes
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: ui-improve
- Module: main.py
- Summary: Add progress dialog for uncached model loading with cancel support
- Reason: Users need feedback during long processing times (48s+) for uncached models
- Alternatives: Status bar text; console output; implemented modal progress dialog
- Risk/Follow-up: Ensure dialog properly handles cancellation and cleanup
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: ui-improve
- Module: main.py
- Summary: Disable all model-related functions when no file is loaded for cleaner UX
- Reason: Users could interact with controls that had no effect, causing confusion
- Alternatives: Hide controls; show tooltips; implemented comprehensive disable logic
- Risk/Follow-up: Ensure controls are properly re-enabled when file is loaded
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: feature-add
- Module: main.py
- Summary: Add enhanced camera movement controls with mouse and keyboard support
- Reason: Basic controls were limited; users need professional 3D navigation
- Alternatives: Trackball controls; arcball; implemented enhanced FPS-style controls
- Risk/Follow-up: Ensure controls work across different systems and mice
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: feature-add
- Module: main.py
- Summary: Add multi-object display in single mode when multiple objects are checked
- Reason: Users want to view selected objects together in original positions without full model mode
- Alternatives: Separate multi-select mode; layer system; implemented checkbox-based selection in single mode
- Risk/Follow-up: Ensure performance with many selected objects and proper LOD handling
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: interface-breaking
- Module: main.py
- Summary: Converted PyQt5 imports to PyQt6 for compatibility
- Reason: PyQt6 was installed and needs to be used instead of PyQt5
- Alternatives: Could have kept PyQt5 but PyQt6 is newer and already installed
- Risk/Follow-up: None - PyQt6 is backward compatible for the used features
- Breaking: yes - requires PyQt6 instead of PyQt5
- Tests Needed: yes - verify application runs correctly with PyQt6

📜 Log Entry
- Date: 2025-11-08
- Type: interface-change
- Module: main.py
- Summary: Enhanced file loading to always trigger Show All mode
- Reason: User requested that opening new files should automatically show all objects
- Alternatives: Could have added a separate setting but automatic activation is more convenient
- Risk/Follow-up: None - improves user experience without breaking existing functionality
- Breaking: no
- Tests Needed: yes - verify new files open in Show All mode correctly

📜 Log Entry
- Date: 2025-11-08
- Type: interface-change
- Module: main.py
- Summary: Enhanced object details panel with prominent size information display
- Reason: User requested better visibility of object/group sizes in the info panel
- Alternatives: Could have added tooltips or hover info but panel display is more persistent
- Risk/Follow-up: None - purely informational enhancement
- Breaking: no
- Tests Needed: yes - verify size calculations display correctly for various objects

