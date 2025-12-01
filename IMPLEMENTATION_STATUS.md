# OCSF Multi-Version Support - Implementation Status

## ✅ Completed Tasks (Phase 1 - Backend Foundation)

### 1. OCSF Version Enum ✅
**File**: `playground/backend/core/ocsf/ocsf_versions.py`
- Added 8 OCSF versions (v1.0.0 through v1.7.0)
- Added helper methods: `get_default()`, `get_latest()`, `get_url_safe_name()`
- Maintains v1.1.0 as default for backward compatibility

### 2. Dynamic Schema Loader ✅
**File**: `playground/backend/core/ocsf/schema_loader.py`
- Created `get_ocsf_schema(version)` - loads any OCSF version
- Created `get_event_classes(version)` - extracts event classes from schema
- Implements caching for performance
- Supports preloading schemas on startup

### 3. Dynamic Event Class System ✅
**File**: `playground/backend/core/ocsf/ocsf_event_classes.py`
- Created `get_event_class_enum(version)` - generates event class enum for any version
- Caches generated enums
- Maintains backward compatibility with v1.1.0

### 4. Expert Definitions Updated ✅
**Files Updated**:
- `playground/backend/categorization_expert/prompting/knowledge/__init__.py`
  - Dynamic OCSF guidance and knowledge generation for all versions
  - Caches generated content for performance

- `playground/backend/entities_expert/prompting/knowledge/__init__.py`
  - Dynamic event class knowledge loading
  - Dynamic schema loading for all versions
  - Falls back to v1.1.0 cached data for performance

- `playground/backend/transformers/validators.py`
  - Refactored `OcsfV1_1_0TransformValidator` → `OcsfTransformValidator`
  - Accepts `ocsf_version` parameter
  - Dynamic schema loading for validation
  - Backward compatibility aliases maintained

## 🔄 Remaining Tasks (Phase 2 - API & Frontend)

### 5. Update API Views & URL Patterns ⏳
**File**: `playground/playground_api/views.py`

**Current hard-coded version usage:**
```python
# Line 148:
expert = get_categorization_expert(OcsfVersion.V1_1_0)

# Line 306:
expert = get_analysis_expert(OcsfVersion.V1_1_0, event_name)

# Line 381:
ocsf_version=OcsfVersion.V1_1_0
```

**Required changes:**
1. Add `ocsf_version` parameter to all relevant request serializers
2. Extract version from request data in views
3. Pass dynamic version to expert instantiation
4. Update all 5 endpoints:
   - `/transformer/categorize/`
   - `/transformer/entities/analyze/`
   - `/transformer/entities/extract/`
   - `/transformer/entities/test/`
   - `/transformer/logic/create/`

**Recommended approach:**
- Make version an optional query parameter (defaults to v1.1.0)
- Example: `/transformer/categorize/?version=1.7.0`
- OR: Keep versioned URLs and add new routes for each version

### 6. Update Serializers ⏳
**File**: `playground/playground_api/serializers.py`

**Current version-specific serializers:**
- `TransformerCategorizeV1_1_0RequestSerializer`
- `TransformerEntitiesV1_1_0AnalyzeRequestSerializer`
- `TransformerEntitiesV1_1_0ExtractRequestSerializer`
- etc.

**Required changes:**
1. Add `ocsf_version` field to request serializers:
   ```python
   ocsf_version = EnumChoiceField(enum=OcsfVersion, default=OcsfVersion.V1_1_0)
   ```

2. Make event class enum selection dynamic:
   ```python
   def validate(self, data):
       version = data.get('ocsf_version', OcsfVersion.V1_1_0)
       EventClassEnum = get_event_class_enum(version)
       # Validate category against version-specific enum
       return data
   ```

3. Update response serializers to include version information

**Complexity**: Medium - requires careful validation logic

### 7. Regenerate OpenAPI Schema & Frontend Client ⏳
**Commands to run:**
```bash
# 1. Regenerate OpenAPI schema from Django
cd playground
pipenv run python3 manage.py spectacular --file schema.json

# 2. Regenerate TypeScript API client
cd ../playground_frontend
npm run generate-api-client
```

**Expected outcome:**
- `OcsfVersionEnum` in frontend with all 8 versions
- Updated API method signatures with version parameters
- Type-safe version selection in TypeScript

### 8. Add Version Selector UI ⏳
**Files to modify:**
- `playground_frontend/src/components/CategoryPanel/CategoryControls.tsx`
- `playground_frontend/src/hooks/useCategoryState.tsx`
- `playground_frontend/src/hooks/useEntitiesState.ts`

**UI Changes needed:**
```tsx
// Add version selector dropdown
<FormField label="OCSF Version">
  <Select
    selectedOption={selectedVersion}
    onChange={({ detail }) => setSelectedVersion(detail.selectedOption)}
    options={ocsfVersionOptions}
    placeholder="Select OCSF version"
  />
</FormField>
```

**State management:**
- Add `selectedVersion` to component state
- Default to v1.1.0
- Pass version to all API calls
- Show version in UI headers/footers

**Complexity**: Low - straightforward React state management

### 9. Testing ⏳
**Test scenarios:**
- [ ] Load schema for each version (v1.0.0 through v1.7.0)
- [ ] Categorize logs with v1.1.0 (existing) ✅
- [ ] Categorize logs with v1.7.0 (latest)
- [ ] Analyze entities with different versions
- [ ] Extract mappings with different versions
- [ ] Generate transformers with different versions
- [ ] Verify event class lists match OCSF schema for each version
- [ ] Test version switching in UI
- [ ] Verify validation works for all versions

**Test command:**
```bash
cd playground
pipenv run python3 manage.py test
```

## Quick Start Guide for Completion

### Step 1: Update Views (30 mins)
```python
# In playground_api/views.py, for each view:

class TransformerCategorizeView(APIView):
    @extend_schema(...)
    def post(self, request):
        serializer = TransformerCategorizeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Get version from request (defaults to v1.1.0)
        ocsf_version = serializer.validated_data.get('ocsf_version', OcsfVersion.V1_1_0)

        # Use dynamic version
        expert = get_categorization_expert(ocsf_version)
        # ... rest of logic
```

### Step 2: Update Serializers (45 mins)
Add version field to each request serializer and make event class validation dynamic.

### Step 3: Regenerate API Client (5 mins)
Run the spectacular and npm commands to regenerate the frontend client.

### Step 4: Add UI Selector (30 mins)
Add Select dropdown in CategoryControls and wire up state management.

### Step 5: Test (1 hour)
Test all endpoints with multiple versions, starting with v1.1.0 (should work unchanged) and v1.7.0 (new).

## Estimated Time to Complete
- **Remaining backend work**: 1.5 hours
- **Frontend work**: 30 minutes
- **Testing**: 1 hour
- **Total**: ~3 hours

## Notes
- v1.1.0 remains default everywhere for backward compatibility
- All dynamic loading includes caching for performance
- SSL certificate issues may occur when loading schemas - test network access first
- Consider preloading schemas at Django startup for production

## Testing the Current Implementation

You can test the completed backend changes now:

```python
# Test in Django shell
cd playground
pipenv run python3 manage.py shell

from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.core.ocsf.schema_loader import get_ocsf_schema, get_event_classes
from backend.core.ocsf.ocsf_event_classes import get_event_class_enum

# Load schema for v1.7.0
schema = get_ocsf_schema(OcsfVersion.V1_7_0)
print(f"Loaded schema version: {schema.version}")

# Get event classes for v1.7.0
events = get_event_classes(OcsfVersion.V1_7_0)
print(f"Found {len(events)} event classes")

# Get event class enum for v1.7.0
EventEnum = get_event_class_enum(OcsfVersion.V1_7_0)
print(f"Generated enum with {len(EventEnum)} members")
```
