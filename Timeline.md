📜 Log Entry
- Date: 2025-11-08
- Type: design-discuss
- Module: docs/
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
- Summary: Change cache location to .cache in project folder (from user home)
- Reason: User preference; avoid using C: or home dir for cache
- Alternatives: ENV-configurable path; CLi flag; postponed
- Risk/Follow-up: Monitor .cache size; add cleanup UI (already present)
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: design-discuss
- Module: model_cache.py
- Summary: Switch cache key to content hash, enabling reuse for copied/renamed files
- Reason: Improve UX and performance; identical files should hit cache
- Alternatives: Path-based cache; dual-key (path+hash); rejected
- Risk/Follow-up: Index can grow with many paths; consider LRU for index entries
- Breaking: no
- Tests Needed: no

📜 Log Entry
- Date: 2025-11-08
- Type: design-discuss
- Module: docs/, README.md
- Summary: Consolidate all documentation into single README.md; delete other .md files
- Reason: Project rule requires only one README and a Timeline; reduce fragmentation
- Alternatives: Keep separate guides under docs/; move to subdirectory; rejected
- Risk/Follow-up: Ensure README remains comprehensive and maintainable
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
- Type: design-discuss
- Module: .gitignore
- Summary: Add *.obj and *.mtl files to gitignore to exclude large 3D model files
- Reason: OBJ files are large binary assets that shouldn't be in version control
- Alternatives: Track sample OBJ files; use LFS; rejected for simplicity
- Risk/Follow-up: Users need to add their own test files locally
- Breaking: no
- Tests Needed: no
