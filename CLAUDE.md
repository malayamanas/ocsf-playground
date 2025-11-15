# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **OCSF Normalization Playground** is a full-stack application for converting log/data entries into OCSF-compliant JSON using GenAI assistance. The architecture consists of:

- **Backend**: Django REST API (`playground/`) with LLM-powered transformation logic
- **Frontend**: Next.js/React web interface (`playground_frontend/`) with TypeScript
- **Experts**: Four specialized LLM-powered modules that handle different transformation aspects

### Key Architecture Components

#### Backend Expert System

The backend is organized around four specialized "experts" that handle different aspects of log normalization:

1. **Regex Expert** (`backend/regex_expert/`): Uses Claude to generate regex patterns that identify specific log entries
2. **Categorization Expert** (`backend/categorization_expert/`): Maps entries to OCSF Event Classes
3. **Entities Expert** (`backend/entities_expert/`): Analyzes which OCSF fields can be extracted/transformed from raw data
4. **Transformers** (`backend/transformers/`): Converts entity mappings into executable transformation logic (currently Python only)

Each expert follows a common pattern:
- `task_def.py`: Defines the task structure and parameters
- `expert_def.py`: Contains expert instantiation and invocation logic
- `tool_def.py`: Defines tools the expert uses (Claude tool_use)
- `prompting/`: Contains system prompts and instructions
- `validators.py`: Post-execution validation (for entities_expert)

#### Core Infrastructure (`backend/core/`)

- `experts.py` & `inference.py`: Base classes for expert definitions and LLM inference
- `ocsf/`: OCSF schema loading and version management (currently v1.1.0)
- `rest_client.py`: Bedrock client for LLM inference
- `validation_report.py`: Data structure for tracking validation results
- `validators.py`: Base validators for transformation outputs

#### Frontend Architecture

Uses Next.js App Router with TypeScript. Key directories:
- `src/app/`: Page routes
- `src/components/`: UI components (Cloudscape Design System)
- `src/generated-api-client/`: Auto-generated TypeScript client (from OpenAPI schema)
- `src/hooks/`: Custom React hooks
- `src/utils/`: Utility functions

The frontend consumes a backend OpenAPI schema auto-generated via `drf-spectacular`.

## Building and Running

### Backend Setup

```bash
# From repo root
python3 -m venv venv
source venv/bin/activate
pipenv sync --dev

# Start Django server
cd playground && python3 manage.py runserver
```

The server runs at `http://127.0.0.1:8000` with logs in `playground/logs/`.

### Frontend Setup

```bash
# From repo root
cd playground_frontend && npm install && npm run dev
```

The web app runs at `http://localhost:3000`.

### Regenerating API Client

When backend API changes, regenerate the OpenAPI schema and TypeScript client:

```bash
# Generate schema from Django
cd playground && python3 manage.py spectacular --file schema.json

# Generate TypeScript client
cd playground_frontend && npm run generate-api-client
```

## Testing

### Backend Tests

Django's built-in test framework with unittest.mock:

```bash
# Run all tests
cd playground && python3 manage.py test

# Run specific test module
cd playground && python3 manage.py test playground_api.tests.test_views

# Run with verbose output
cd playground && python3 manage.py test -v 2
```

Test files are in `playground_api/tests/` and `backend/core/tests/`. Current test coverage includes:
- View/API tests (`test_views.py`)
- Serializer tests (`test_serializers.py`)
- REST client tests (`backend/core/tests/test_rest_client.py`)

### Frontend Tests

No automated tests currently configured. Linting and formatting:

```bash
# Lint
cd playground_frontend && npm run lint

# Auto-fix linting and formatting
cd playground_frontend && npm run lint:fix
```

## Development Workflow

### Adding Backend Endpoints

1. Create serializers in `playground_api/serializers.py`
2. Add view class in `playground_api/views.py` (inherits from `APIView`)
3. Register routes in `playground/urls.py`
4. Run `drf-spectacular` to regenerate schema
5. Regenerate frontend API client
6. Add tests in `playground_api/tests/`

### Modifying Experts

Each expert (`regex_expert`, `categorization_expert`, `entities_expert`) follows this pattern:

1. Update `task_def.py` if parameters change
2. Update prompts in `prompting/` directory
3. Update `tool_def.py` if tools have changed
4. Update `expert_def.py` invocation logic if needed
5. Add validation logic to `validators.py` if new output needs validation

### Working with OCSF Schema

The OCSF schema is loaded from the `ocsf-lib-py` package at `backend/core/ocsf/ocsf_versions.py`. To update the OCSF version:

```bash
# Generate new schema version
python3 -m ocsf.schema 1.5.0 > schema.json

# Update version reference in ocsf_versions.py
```

## Key Dependencies and Configurations

### Backend Dependencies (Pipfile)

- **Django + DRF**: Web framework and REST API
- **Anthropic**: Claude API client for LLM inference
- **LangChain + langchain-core**: LLM interface abstraction and task orchestration
- **ocsf-lib**: OCSF schema definitions
- **drf-spectacular**: OpenAPI schema generation

### Frontend Dependencies (package.json)

- **Next.js 15**: React framework with App Router
- **Cloudscape Design System**: AWS UI component library
- **Tailwind CSS**: Utility-first CSS
- **Ace Editor**: Code editor component (via ace-builds)
- **OpenAPI Generator**: Generate TypeScript API client

### Claude Authentication

The backend uses the **Claude CLI** (`claude` binary) instead of the Anthropic API. This means you don't need an API key - it uses your existing Claude Code authentication!

**Setup:**
```bash
# Make sure claude is authenticated (you should already have done this)
claude --version

# Start the server - no API key needed!
cd playground
python3 manage.py runserver
```

**How it works:**
- The backend calls the `claude` CLI binary directly for all LLM operations
- Authentication is handled automatically by the Claude CLI using your Claude Code subscription
- No environment variables needed!
- No API keys to manage!

**Advantages:**
- ✅ No Anthropic API key required
- ✅ Uses your existing Claude Code subscription
- ✅ Authentication handled automatically by Claude CLI
- ✅ Same models and capabilities as the API

**Models used:**
- All experts now use: `claude-sonnet-4-5-20250514` (Claude 4.5 Sonnet)

## Important Caveats and Known Issues

### Token Usage

The `Analyze Entities` endpoint uses extensive tokens (tens of thousands) because it passes the full OCSF Event Class spec to Claude. It uses Claude 3.7 in "Thinking Mode" for improved accuracy. This can cause throttling and long response times. The `Extract Entity Mappings` uses fewer tokens by only passing relevant OCSF spec sections.

### Validation Limitations

Current validation only verifies transform functions can load/execute. Full OCSF spec compliance validation (type checking) is not yet implemented but should be straightforward using type information available in the spec.

### Single Language/Version Support

- **Transform Language**: Python only (straightforward to add others)
- **OCSF Version**: v1.1.0 only (easy to extend using existing code pathways)

## Debugging

### Backend Logs

Logs are written to `playground/logs/` directory. Check these when inference fails or validation has issues.

### Testing Endpoints via curl

Example backend API calls from the README:

```bash
# Heuristic (regex) generation
curl -X POST "http://127.0.0.1:8000/transformer/heuristic/create/" \
  -H "Content-Type: application/json" \
  -d '{"input_entry": "..."}'

# Categorization
curl -X POST "http://127.0.0.1:8000/transformer/categorize/v1_1_0/" \
  -H "Content-Type: application/json" \
  -d '{"input_entry": "..."}'

# Entity analysis
curl -X POST "http://127.0.0.1:8000/transformer/entities/v1_1_0/analyze/" \
  -H "Content-Type: application/json" \
  -d '{"ocsf_category": "...", "input_entry": "..."}'
```
