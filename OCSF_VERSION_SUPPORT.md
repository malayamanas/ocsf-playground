# OCSF Multi-Version Support Implementation

This document describes the implementation of multi-version OCSF schema support for the OCSF Normalization Playground.

## Current Status

### ✅ Completed

1. **Added Multiple OCSF Versions** (`backend/core/ocsf/ocsf_versions.py`)
   - Added support for OCSF versions: v1.0.0, v1.1.0, v1.2.0, v1.3.0, v1.4.0, v1.5.0, v1.6.0, v1.7.0
   - v1.7.0 is the latest stable version
   - v1.1.0 remains the default for backward compatibility
   - Added helper methods: `get_default()`, `get_latest()`, `get_url_safe_name()`

2. **Created Dynamic Schema Loader** (`backend/core/ocsf/schema_loader.py`)
   - Loads OCSF schemas dynamically for any version using `ocsf-lib-py`
   - Caches loaded schemas for performance
   - Provides `get_ocsf_schema(version)` and `get_event_classes(version)`
   - Supports cache management and preloading

3. **Updated Event Class System** (`backend/core/ocsf/ocsf_event_classes.py`)
   - Added `get_event_class_enum(version)` function
   - Dynamically generates event class enums for any OCSF version
   - Maintains backward compatibility with v1.1.0
   - Caches generated enums for performance

### ⏳ Remaining Work

The following tasks are required to fully implement multi-version support:

#### 1. Update Expert Definitions
**Files to modify:**
- `playground/backend/categorization_expert/expert_def.py`
- `playground/backend/entities_expert/expert_def.py`

**Changes needed:**
- Update `get_categorization_expert(version)` to use dynamic event class enums
- Update `get_analysis_expert(version, event_name)` to use dynamic schemas
- Update prompting/knowledge modules to work with any version

#### 2. Update API Views
**File to modify:**
- `playground/playground_api/views.py`

**Changes needed:**
- Make version parameter dynamic instead of hard-coded `OcsfVersion.V1_1_0`
- Support version selection via request parameters or URL path
- Update all expert instantiations to use the requested version

**Current hard-coded occurrences:**
```python
# Line 148:
expert = get_categorization_expert(OcsfVersion.V1_1_0)

# Line 306:
expert = get_analysis_expert(OcsfVersion.V1_1_0, event_name)

# Line 381:
ocsf_version=OcsfVersion.V1_1_0
```

#### 3. Update URL Patterns
**File to modify:**
- `playground/playground/urls.py`

**Options:**
- **Option A**: Keep version-specific URLs (e.g., `/transformer/categorize/v1_1_0/`)
  - Add routes for each new version
  - Example: `/transformer/categorize/v1_7_0/`

- **Option B**: Make version a query parameter (recommended)
  - Change to: `/transformer/categorize/?version=1.7.0`
  - More flexible, easier to maintain

#### 4. Update Serializers
**File to modify:**
- `playground/playground_api/serializers.py`

**Changes needed:**
- Update serializers to accept `ocsf_version` as input parameter
- Make event class enum selection dynamic based on version
- Current serializers use `EnumChoiceField(enum=OcsfEventClassesV1_1_0)` which needs to be dynamic

**Example change:**
```python
# Before:
class TransformerCategorizeV1_1_0RequestSerializer(serializers.Serializer):
    ocsf_category = EnumChoiceField(enum=OcsfEventClassesV1_1_0)

# After:
class TransformerCategorizeRequestSerializer(serializers.Serializer):
    ocsf_version = EnumChoiceField(enum=OcsfVersion, default=OcsfVersion.V1_1_0)
    # ocsf_category validation will need to be dynamic based on version
```

#### 5. Regenerate OpenAPI Schema and Frontend Client
**Commands:**
```bash
# Generate OpenAPI schema
cd playground
python3 manage.py spectacular --file schema.json

# Generate TypeScript API client
cd ../playground_frontend
npm run generate-api-client
```

**Result:**
- Frontend will have updated types with all OCSF versions
- `OcsfVersionEnum` will include all versions
- API client methods will accept version parameters

#### 6. Add Version Selector UI
**Files to modify:**
- `playground_frontend/src/components/CategoryPanel/CategoryControls.tsx`
- `playground_frontend/src/hooks/useCategoryState.tsx`
- `playground_frontend/src/hooks/useEntitiesState.ts`

**Changes needed:**
- Add a Select component for OCSF version selection
- Default to v1.1.0 for backward compatibility
- Store selected version in state
- Pass version to all API calls
- Display selected version in UI

**Example UI component:**
```tsx
<FormField label="OCSF Version">
  <Select
    selectedOption={selectedVersion}
    onChange={({ detail }) => setSelectedVersion(detail.selectedOption)}
    options={ocsfVersionOptions}
    placeholder="Select OCSF version"
  />
</FormField>
```

#### 7. Testing
**Test scenarios:**
- [ ] Load schemas for each OCSF version
- [ ] Categorize log entries with different versions
- [ ] Analyze entities with different versions
- [ ] Extract entity mappings with different versions
- [ ] Generate transformers with different versions
- [ ] Verify event class lists are correct for each version
- [ ] Test version switching in UI
- [ ] Verify backward compatibility with v1.1.0

## Architecture

### Data Flow

```
User selects OCSF version in UI
         ↓
Frontend sends version with API request
         ↓
Backend receives version parameter
         ↓
schema_loader.get_ocsf_schema(version)
         ↓
Cached or fetch from OCSF API
         ↓
event_classes.get_event_class_enum(version)
         ↓
Expert uses version-specific schema
         ↓
Generate transformation logic for version
         ↓
Return OCSF JSON matching selected version
```

### Schema Loading

```python
from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.core.ocsf.schema_loader import get_ocsf_schema, get_event_classes
from backend.core.ocsf.ocsf_event_classes import get_event_class_enum

# Get schema for a specific version
schema_v1_7_0 = get_ocsf_schema(OcsfVersion.V1_7_0)

# Get event classes for a version
events_v1_7_0 = get_event_classes(OcsfVersion.V1_7_0)

# Get event class enum for a version
EventClassEnum = get_event_class_enum(OcsfVersion.V1_7_0)
```

## Migration Guide

### For Developers

1. **Update code to use dynamic version:**
   ```python
   # Old:
   from backend.core.ocsf.ocsf_event_classes import OcsfEventClassesV1_1_0
   expert = get_categorization_expert(OcsfVersion.V1_1_0)

   # New:
   from backend.core.ocsf.ocsf_event_classes import get_event_class_enum
   EventClassEnum = get_event_class_enum(requested_version)
   expert = get_categorization_expert(requested_version)
   ```

2. **Update API calls to include version:**
   ```typescript
   // Old:
   await client.transformerCategorizeV110Create({ input_entry: log });

   // New:
   await client.transformerCategorizeCreate({
     ocsf_version: selectedVersion,
     input_entry: log
   });
   ```

### For Users

1. **Select OCSF version** from dropdown in UI (default: v1.1.0)
2. **All transformations** will use the selected version
3. **Version compatibility**: Generated transformers are version-specific
4. **Recommendation**: Use v1.7.0 for new projects (latest stable)

## Performance Considerations

- **Schema caching**: Schemas are loaded once and cached in memory
- **Network latency**: First load for each version requires download from OCSF API
- **Preloading**: Optional `preload_schemas()` can warm cache at startup
- **Memory usage**: Each schema is ~1-5MB, minimal impact

## Known Limitations

1. **SSL Certificate Issue**: Some environments may have SSL verification issues when downloading schemas
   - Workaround: Download schemas manually and load from file
   - See: https://github.com/ocsf/ocsf-lib-py

2. **Version Differences**: Some event classes/fields may differ between versions
   - Generated transformers may need adjustments when switching versions
   - Test transformations after version changes

3. **Backward Compatibility**: v1.1.0 remains default to avoid breaking existing integrations

## References

- **OCSF Schema Browser**: https://schema.ocsf.io/
- **OCSF GitHub**: https://github.com/ocsf
- **ocsf-lib-py**: https://github.com/ocsf/ocsf-lib-py
- **OCSF Changelog**: https://schema.ocsf.io/changelog

## Next Steps

1. Complete remaining implementation tasks (see "Remaining Work" above)
2. Add integration tests for multi-version support
3. Update user documentation with version selection guide
4. Consider adding version comparison feature in UI
5. Add migration tool to convert transformers between versions
