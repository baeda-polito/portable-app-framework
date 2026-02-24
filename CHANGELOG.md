## [0.1.11] - 2024-07-01

- Fixed building motif validation for qualify function

## [0.1.12] - 2026-02-24

### Added
- Optional `base_path` parameter to `Application` class to support execution from non-root directories.
- Warning log when no applications are found in the resolved `app/` folder.

### Fixed
- Robustness of file existence checks in `Application` initialization (switched from `is None` to `os.path.exists()`).
- Corrected path resolution for `query.rq` and `manifest.ttl`.