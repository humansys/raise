# Complete Software Development Cycle Guide: Cursor 2.0 for Multi-Stack Applications

## Executive Summary

This guide provides a comprehensive workflow for developing a multi-stack application using Cursor 2.0, specifically optimized for a **Pydantic-AI backend**, **PHP Laravel admin interface**, and **Svelte frontend**. The guide leverages Cursor 2.0's revolutionary features including Composer model, parallel agents, built-in browser, voice mode, and agent-first interface to maximize development speed.

---

## Table of Contents

1. [Initial Setup & Configuration](#1-initial-setup--configuration)
2. [Project Structure & Organization](#2-project-structure--organization)
3. [Phase 1: Planning & Architecture](#3-phase-1-planning--architecture)
4. [Phase 2: Backend Development (Pydantic-AI)](#4-phase-2-backend-development-pydantic-ai)
5. [Phase 3: Admin Interface Development (Laravel)](#5-phase-3-admin-interface-development-laravel)
6. [Phase 4: Frontend Development (Svelte)](#6-phase-4-frontend-development-svelte)
7. [Phase 5: Integration & Testing](#7-phase-5-integration--testing)
8. [Phase 6: Debugging & Optimization](#8-phase-6-debugging--optimization)
9. [Phase 7: Documentation & Code Review](#9-phase-7-documentation--code-review)
10. [Phase 8: Deployment](#10-phase-8-deployment)
11. [Advanced Cursor 2.0 Features](#11-advanced-cursor-20-features)
12. [Best Practices & Pro Tips](#12-best-practices--pro-tips)

---

## 1. Initial Setup & Configuration

### 1.1 Install Cursor 2.0

Download Cursor 2.0 from [cursor.com](https://cursor.com) and ensure you're on the latest version with access to:
- Composer model (native coding model)
- Built-in browser feature
- Parallel agents
- Voice mode
- MCP (Model Context Protocol) support

### 1.2 Global Cursor Settings

**Access Settings**: `Cursor > Settings > Cursor Settings` or `Cmd/Ctrl + Shift + P` → "Cursor Settings"

#### Enable Key Features:
```
Features > Chat & Composer:
✓ Enable Agent mode
✓ Enable Composer
✓ Enable Browser (Beta)
✓ Enable Voice Mode
✓ Enable YOLO mode (for experienced users - allows autonomous command execution)
```

#### Model Configuration:
- **Plan Mode**: Use Claude 3.5 Sonnet or GPT-4 for architectural planning
- **Agent Mode (Build)**: Use Composer (Cursor's native model) for 4x faster code generation
- **Quick Edits**: Use Claude 3.5 Haiku or GPT-4o-mini for speed

**Pro Tip**: You can switch models mid-conversation without losing context.

### 1.3 Configure Global AI Rules

Navigate to: `Cursor Settings > Features > Chat & Composer > Rules for AI`

Add these global rules:

```markdown
# Global Development Standards

## General Principles
- Write clean, maintainable, production-ready code
- Follow DRY (Don't Repeat Yourself) principles
- Use descriptive variable and function names
- Prioritize code readability over premature optimization
- Include error handling and logging
- Write tests for all new features
- Add clear comments for complex logic

## Code Style
- Use consistent indentation (2 spaces for JS/TS, 4 for Python/PHP)
- Follow language-specific style guides (PEP 8 for Python, PSR-12 for PHP)
- Use modern language features (Python 3.11+, PHP 8.1+, ES6+)
- Avoid magic numbers and hardcoded values

## Security
- Validate all user inputs
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Store secrets in environment variables
- Never commit sensitive data

## Documentation
- Write clear docstrings/comments for functions and classes
- Keep README files updated
- Document API endpoints with request/response examples
```

### 1.4 Configure Terminal Settings

```
Cursor Settings > Features > Terminal:
✓ Allow Agent to use native terminal
✓ Share terminal with Agent
✓ Enable sandboxed terminals (for safe execution)
```

### 1.5 Install Essential Extensions

Since Cursor is based on VS Code, install these extensions:

**For Python/Pydantic-AI:**
- Python (Microsoft)
- Pylance
- Python Environment Manager

**For PHP/Laravel:**
- Laravel Extension Pack
- PHP Intelephense
- Laravel Blade Snippets

**For Svelte:**
- Svelte for VS Code
- Svelte Intellisense
- Svelte 3 Snippets

**General:**
- GitLens
- ESLint
- Prettier
- Docker
- Thunder Client (API testing)

---

## 2. Project Structure & Organization

### 2.1 Recommended Monorepo Structure

Create this structure for your multi-stack application:

```
your-project/
├── .cursor/                    # Cursor-specific configuration
│   ├── rules/                  # Project-specific AI rules
│   │   ├── backend.mdc         # Backend-specific rules
│   │   ├── admin.mdc           # Admin interface rules
│   │   ├── frontend.mdc        # Frontend rules
│   │   └── testing.mdc         # Testing standards
│   ├── commands/               # Custom slash commands
│   │   ├── code-review.md
│   │   ├── run-tests.md
│   │   └── deploy.md
│   ├── mcp.json               # MCP server configuration
│   └── environment.json        # Cloud environment config
├── .cursorrules               # Main project rules file
├── backend/                   # Pydantic-AI backend
│   ├── src/
│   │   ├── agents/            # Pydantic-AI agents
│   │   ├── models/            # Data models
│   │   ├── api/               # FastAPI/Flask routes
│   │   ├── services/          # Business logic
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── admin/                     # Laravel admin interface
│   ├── app/
│   │   ├── Http/
│   │   │   ├── Controllers/
│   │   │   └── Middleware/
│   │   ├── Models/
│   │   └── Services/
│   ├── resources/
│   │   └── views/
│   ├── routes/
│   ├── tests/
│   └── composer.json
├── frontend/                  # Svelte frontend
│   ├── src/
│   │   ├── routes/            # SvelteKit routes
│   │   ├── lib/
│   │   │   ├── components/    # Reusable components
│   │   │   ├── stores/        # Svelte stores
│   │   │   └── utils/
│   │   └── app.html
│   ├── static/
│   ├── tests/
│   └── package.json
├── docs/                      # Project documentation
│   ├── requirements/          # PRDs and specifications
│   │   ├── project-overview.md
│   │   ├── backend-spec.md
│   │   ├── admin-spec.md
│   │   └── frontend-spec.md
│   ├── architecture/
│   │   ├── system-design.md
│   │   ├── api-contracts.md
│   │   └── database-schema.md
│   └── temp/                  # Working documentation
│       ├── current-state.md
│       └── decisions.md
├── shared/                    # Shared types/contracts
│   ├── types/
│   └── contracts/
├── docker-compose.yml
├── .gitignore
└── README.md
```

### 2.2 Create .cursorrules File

In your project root, create `.cursorrules`:

```markdown
# Project-Specific Rules for Multi-Stack Application

## Project Overview
This is a multi-stack application with:
- Backend: Pydantic-AI (Python 3.11+) with FastAPI
- Admin: Laravel 11+ (PHP 8.2+) with Blade templates
- Frontend: SvelteKit 2.0+ with TypeScript and TailwindCSS

## Stack Technologies
### Backend (Pydantic-AI)
- Python 3.11+
- Pydantic-AI for agent workflows
- FastAPI for REST API
- PostgreSQL database
- Redis for caching
- Celery for background tasks

### Admin (Laravel)
- PHP 8.2+
- Laravel 11+
- Blade templating
- Breeze/Jetstream for auth
- Livewire for reactive components

### Frontend (Svelte)
- SvelteKit 2.0+
- TypeScript
- TailwindCSS
- Svelte stores for state management
- SvelteKit form actions

## File Organization Rules

### Backend
- Place agents in `backend/src/agents/`
- Place models in `backend/src/models/`
- Place API routes in `backend/src/api/`
- Use snake_case for Python files and variables
- Name files descriptively: `user_agent.py`, `auth_service.py`

### Admin
- Controllers in `admin/app/Http/Controllers/`
- Follow Laravel naming conventions
- Use PascalCase for class names
- Use camelCase for methods
- Blade views in `admin/resources/views/`

### Frontend
- Components in `frontend/src/lib/components/`
- Use PascalCase for component files: `UserProfile.svelte`
- Routes in `frontend/src/routes/`
- Use route folders for pages: `routes/dashboard/+page.svelte`

## API Communication
- Backend exposes REST API at `/api/v1/`
- Admin communicates with backend via HTTP client
- Frontend uses SvelteKit load functions for SSR data fetching
- All endpoints documented in `docs/architecture/api-contracts.md`

## Coding Standards

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints everywhere
- Use async/await for I/O operations
- Use Pydantic models for validation
- Structure: models → services → agents → API

### Admin (Laravel)
- Follow PSR-12 coding standards
- Use Service/Repository pattern
- Implement Form Requests for validation
- Use Eloquent ORM (not raw queries)
- Follow MVC architecture strictly

### Frontend (Svelte)
- Use TypeScript with strict mode
- Use SvelteKit's load functions for data fetching
- Use form actions for mutations
- Prefer composition over inheritance
- Use Svelte stores for global state
- Use `$lib` alias for imports

## Testing Requirements
- Backend: pytest with >80% coverage
- Admin: PHPUnit with Feature and Unit tests
- Frontend: Vitest for unit tests, Playwright for E2E
- Test files next to source files or in dedicated `tests/` folder

## Security Requirements
- Use environment variables for all secrets
- Implement CSRF protection
- Sanitize all user inputs
- Use parameterized queries
- Implement rate limiting on APIs
- Use HTTPS in production

## Git Workflow
- Feature branches: `feature/description`
- Bugfix branches: `bugfix/description`
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
- Commit frequently with clear messages
```

---

## 3. Phase 1: Planning & Architecture

### 3.1 Create Product Requirements Document (PRD)

Create `docs/requirements/project-overview.md`:

**Use Cursor Agent to Help:**
Open Cursor Composer (`Cmd/Ctrl + I`) and prompt:

```
I need to create a comprehensive PRD for a multi-stack application. 
The application should [describe your app purpose and key features].

Create a structured PRD document that includes:
1. Project overview and goals
2. User personas and use cases
3. Feature list with priorities
4. Non-functional requirements
5. Success metrics

Save this as docs/requirements/project-overview.md
```

### 3.2 Define System Architecture

Create `docs/architecture/system-design.md`:

```
@agent Create a system architecture document for our multi-stack application.

Context:
- Backend: Pydantic-AI agents with FastAPI
- Admin: Laravel for content management
- Frontend: SvelteKit for user-facing app

Include:
1. High-level architecture diagram (describe in text/ASCII)
2. Component interactions
3. Data flow between services
4. Authentication/authorization strategy
5. Caching strategy
6. Error handling approach
```

### 3.3 Define API Contracts

Create `docs/architecture/api-contracts.md`:

```
@agent Create an API contract document that defines all REST endpoints.

For each endpoint include:
- HTTP method and path
- Request parameters and body schema
- Response schema (success and error cases)
- Authentication requirements
- Example requests and responses

Organize by feature domain (auth, users, content, etc.)
```

**Pro Tip**: Save this as a reference file. You'll use `@Codebase` and reference this file frequently.

### 3.4 Design Database Schema

Create `docs/architecture/database-schema.md`:

**Use Parallel Agents** for different perspectives:

1. Open Cursor Composer
2. Click the parallel agents icon (if available) or create multiple composer sessions
3. Run the same prompt with different models:

```
@agent Design the PostgreSQL database schema for our application.

Requirements:
- User management with roles
- [Your specific entities]
- Relationships between entities
- Indexes for performance
- Audit fields (created_at, updated_at)

Provide:
1. ER diagram (text description)
2. SQL CREATE statements
3. Migration strategy
```

Compare outputs and merge the best ideas.

---

## 4. Phase 2: Backend Development (Pydantic-AI)

### 4.1 Project Initialization

**Use Agent Mode for Setup:**

```
@agent Initialize a Python backend project with Pydantic-AI and FastAPI.

Structure:
backend/
├── src/
│   ├── agents/
│   ├── models/
│   ├── api/
│   ├── services/
│   └── main.py
├── tests/
├── requirements.txt
└── README.md

Include:
- FastAPI setup with CORS
- Pydantic models
- Database connection (async SQLAlchemy)
- Environment variable configuration
- Basic project structure

Use Python 3.11+ features and async/await patterns.
```

### 4.2 Configure Pydantic-AI Documentation Context

Add Pydantic-AI docs to Cursor context:

1. Go to `Cursor Settings > Features > Chat & Composer > Docs`
2. Click "Add New Doc"
3. Enter:
   - Name: "Pydantic AI"
   - URL: `https://ai.pydantic.dev`

Now you can use `@Docs Pydantic AI` in prompts for accurate, up-to-date information.

### 4.3 Create .cursor/rules/backend.mdc

```markdown
---
description: Backend development rules for Pydantic-AI
trigger: agent_requested
---

# Backend Development Rules

## Pydantic-AI Specific
- Use Pydantic AI's Agent class for all AI agents
- Define tools as decorated functions
- Use dependency injection for agent dependencies
- Structure agents in separate files in `src/agents/`
- Use async/await for all I/O operations
- Handle agent errors gracefully with try/except

## FastAPI Standards
- Use FastAPI's dependency injection
- Define routes with proper HTTP methods
- Use Pydantic models for request/response validation
- Implement proper error responses with status codes
- Use router prefixes for organization: `/api/v1/users`

## Database Operations
- Use async SQLAlchemy for database operations
- Define models in `src/models/`
- Use Alembic for migrations
- Implement connection pooling
- Use transactions for multi-step operations

## Testing
- Use pytest with pytest-asyncio
- Test agents with mock dependencies
- Achieve >80% code coverage
- Test API endpoints with TestClient
- Use fixtures for common setup

## Code Example Pattern
```python
# src/agents/user_agent.py
from pydantic_ai import Agent
from pydantic import BaseModel

class UserQuery(BaseModel):
    query: str

class UserResponse(BaseModel):
    answer: str
    confidence: float

user_agent = Agent(
    model='openai:gpt-4',
    system_prompt="You are a helpful user support agent.",
    retries=2
)

@user_agent.tool
async def get_user_info(user_id: int) -> dict:
    """Retrieve user information from database."""
    # Implementation
    pass
```
```

### 4.4 Development Workflow with Cursor

**Step 1: Create Pydantic Models**

Open Composer (`Cmd + I`), switch to **Agent mode**, and prompt:

```
Create Pydantic models for our user management system in backend/src/models/user.py

Requirements:
- User model with id, email, name, role, created_at, updated_at
- Role model with id, name, permissions
- Use appropriate Pydantic field validators
- Include relationship definitions
- Add docstrings

Reference: @docs/architecture/database-schema.md
```

**Step 2: Build FastAPI Routes**

```
@agent Create FastAPI routes for user management in backend/src/api/users.py

Include endpoints:
- POST /api/v1/users (create user)
- GET /api/v1/users/{id} (get user)
- GET /api/v1/users (list users with pagination)
- PUT /api/v1/users/{id} (update user)
- DELETE /api/v1/users/{id} (delete user)

Use:
- Proper HTTP status codes
- Request validation with Pydantic
- Error handling
- Authentication dependency

Reference: @docs/architecture/api-contracts.md
```

**Step 3: Implement Pydantic-AI Agents**

```
@agent Create a Pydantic-AI agent for user support queries in backend/src/agents/support_agent.py

The agent should:
- Answer user questions about their account
- Access user data via tools
- Provide helpful, context-aware responses
- Log interactions for audit

Include:
- Agent definition with system prompt
- Tools for database queries
- Error handling
- Type hints and docstrings

Use @Docs Pydantic AI for latest API patterns
```

**Step 4: Test-Driven Development**

Enable **YOLO mode** for faster iteration, or use the standard approval flow:

```
@agent Create pytest tests for the user API endpoints in backend/tests/test_api_users.py

Include tests for:
- Successful user creation
- Validation errors
- Authentication failures
- Edge cases (duplicate email, invalid ID)
- Database rollback on errors

Use pytest fixtures for test database and client setup
```

**Run tests immediately:**

Cursor Agent can run terminal commands. After creating tests:

```
@agent Run the pytest tests for the user API and fix any failures.

Continue this loop:
1. Run: pytest backend/tests/test_api_users.py -v
2. If failures occur, analyze the error
3. Fix the code
4. Rerun tests
5. Repeat until all tests pass
```

### 4.5 Use Built-in Browser for API Testing

**New in Cursor 2.0**: Test your APIs visually!

1. Start your FastAPI development server:
   ```bash
   cd backend && uvicorn src.main:app --reload
   ```

2. Open Cursor Browser:
   - In Composer, type `@Browser`
   - Or click the browser icon in the Composer panel

3. Navigate to your API docs:
   ```
   @Browser Open http://localhost:8000/docs and test the POST /api/v1/users endpoint with sample data
   ```

4. Cursor Agent can:
   - Interact with the Swagger UI
   - Fill in forms
   - Capture responses
   - Report errors
   - Iterate fixes automatically

5. Debug in real-time:
   ```
   @Browser Test the user creation endpoint. If there are errors, show me the response and suggest fixes.
   ```

### 4.6 Voice Mode for Rapid Development

**Enable Voice Mode**: Click the microphone icon in Composer or press the designated hotkey.

Use voice commands for faster workflow:

- "Create a new Pydantic-AI agent for content moderation"
- "Add error handling to the user service"
- "Run all backend tests and show me the coverage report"
- "Refactor the authentication middleware to use JWT tokens"

Voice mode is excellent for:
- Exploratory coding
- Rapid prototyping
- Hands-free code review
- Quick debugging sessions

---

## 5. Phase 3: Admin Interface Development (Laravel)

### 5.1 Project Initialization

```
@agent Initialize a Laravel 11 admin interface project.

Setup:
admin/
├── app/
│   ├── Http/Controllers/
│   ├── Models/
│   └── Services/
├── resources/views/
├── routes/
└── tests/

Include:
- Laravel Breeze for authentication
- Basic admin dashboard
- User management CRUD
- Middleware for admin access
- Database configuration
- .env.example file

Use Laravel 11+ features and best practices.
```

### 5.2 Configure Laravel-Specific Rules

Create `.cursor/rules/admin.mdc`:

```markdown
---
description: Laravel admin interface development rules
trigger: agent_requested
---

# Laravel Admin Development Rules

## Laravel Conventions
- Follow PSR-12 coding standards
- Use Eloquent ORM (never raw SQL unless necessary)
- Implement Form Requests for validation
- Use Service classes for business logic
- Controllers should be thin (delegate to Services)
- Use Resource Controllers for CRUD operations

## File Organization
- Controllers: `app/Http/Controllers/Admin/`
- Models: `app/Models/`
- Services: `app/Services/`
- Form Requests: `app/Http/Requests/`
- Views: `resources/views/admin/`

## Naming Conventions
- Controllers: `UserController` (singular)
- Models: `User` (singular)
- Tables: `users` (plural)
- Methods: camelCase
- Routes: kebab-case (`/admin/users`)

## API Communication
- Use Guzzle HTTP client to communicate with backend API
- Create service classes for API calls: `app/Services/BackendApiService.php`
- Handle API errors gracefully
- Cache API responses when appropriate
- Use environment variables for API base URL

## Security
- Validate all inputs with Form Requests
- Use CSRF protection (enabled by default)
- Implement role-based access control
- Sanitize outputs in Blade templates
- Use prepared statements with Eloquent

## Testing
- Feature tests for HTTP requests
- Unit tests for Services
- Use database transactions in tests
- Mock external API calls
- Test authentication and authorization

## Code Example
```php
// app/Services/BackendApiService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;

class BackendApiService
{
    private string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = config('services.backend.url');
    }

    public function getUsers(int $page = 1): array
    {
        $response = Http::withToken(auth()->user()->api_token)
            ->get("{$this->baseUrl}/api/v1/users", [
                'page' => $page,
            ]);

        if ($response->failed()) {
            throw new \Exception('Failed to fetch users');
        }

        return $response->json();
    }
}
```
```

### 5.3 Development Workflow

**Step 1: Create Controllers**

```
@agent Create an Admin UserController in app/Http/Controllers/Admin/UserController.php

Include methods:
- index (list users with pagination)
- create (show create form)
- store (save new user)
- edit (show edit form)
- update (save changes)
- destroy (delete user)

The controller should:
- Use BackendApiService to communicate with the backend
- Handle API errors gracefully
- Return appropriate views
- Flash success/error messages
- Follow Laravel conventions

Reference: @.cursor/rules/admin.mdc
```

**Step 2: Create Blade Views**

```
@agent Create Blade views for user management in resources/views/admin/users/

Create:
- index.blade.php (user list with search and pagination)
- create.blade.php (create user form)
- edit.blade.php (edit user form)
- _form.blade.php (shared form partial)

Use:
- TailwindCSS for styling
- Blade components for reusability
- Form validation error display
- CSRF tokens in forms
- Laravel Mix for asset compilation
```

**Step 3: Define Routes**

```
@agent Create admin routes in routes/web.php

Include:
- Authentication routes (Breeze)
- Admin middleware group
- Resource routes for users
- Dashboard route

Ensure all routes are protected by auth and admin middleware
```

**Step 4: Create Service Layer**

```
@agent Create BackendApiService in app/Services/BackendApiService.php

This service should:
- Handle all HTTP communication with the backend API
- Use Laravel HTTP client
- Include methods for all backend endpoints
- Handle authentication with API tokens
- Retry failed requests (up to 3 times)
- Log API errors
- Return typed responses

Reference: @docs/architecture/api-contracts.md for endpoint definitions
```

### 5.4 Testing Laravel Admin

```
@agent Create Feature tests for the Admin UserController in tests/Feature/Admin/UserControllerTest.php

Test:
- Authenticated users can access user list
- Users can create new users via form
- Validation errors are shown
- Users can edit existing users
- Users can delete users
- Unauthenticated users are redirected

Mock the BackendApiService to avoid real API calls
```

**Run tests with Cursor Agent:**

```
@agent Run Laravel tests and fix any failures:

php artisan test --filter=UserControllerTest

If failures occur, analyze and fix the code, then rerun tests.
```

### 5.5 Preview Admin Interface in Browser

**Use Cursor 2.0 Built-in Browser:**

1. Start Laravel development server:
   ```bash
   cd admin && php artisan serve
   ```

2. Open in Cursor Browser:
   ```
   @Browser Open http://localhost:8000/admin and login with test credentials.
   
   Then navigate through:
   - Dashboard
   - User list
   - User creation form
   - User edit form
   
   Report any UI issues, broken links, or styling problems.
   ```

3. **Interactive Debugging**:
   ```
   @Browser Click the "Create User" button, fill in the form with:
   - Email: test@example.com
   - Name: Test User
   - Role: Admin
   
   Submit the form. If there are validation errors, show them to me and suggest fixes.
   ```

4. **Element Inspection**:
   ```
   @Browser Inspect the user table on the index page. Select the "Email" column header and suggest improvements for sorting functionality.
   ```

---

## 6. Phase 4: Frontend Development (Svelte)

### 6.1 Project Initialization

```
@agent Initialize a SvelteKit 2.0 frontend project with TypeScript and TailwindCSS.

Structure:
frontend/
├── src/
│   ├── routes/
│   │   ├── +layout.svelte
│   │   ├── +page.svelte
│   │   └── dashboard/
│   ├── lib/
│   │   ├── components/
│   │   ├── stores/
│   │   └── utils/
│   └── app.html
├── static/
├── tests/
└── package.json

Setup:
- SvelteKit with TypeScript
- TailwindCSS configuration
- Path aliases ($lib)
- Vitest for testing
- Prettier and ESLint
```

### 6.2 Configure Svelte-Specific Rules

Create `.cursor/rules/frontend.mdc`:

```markdown
---
description: Svelte frontend development rules
trigger: agent_requested
---

# Svelte Frontend Development Rules

## SvelteKit Conventions
- Use TypeScript with strict mode
- File-based routing in `src/routes/`
- Use `+page.svelte` for pages
- Use `+layout.svelte` for layouts
- Use `+page.ts` or `+page.server.ts` for data loading
- Use `+server.ts` for API endpoints (if needed)

## Component Structure
- Components in `src/lib/components/`
- Use PascalCase for component files: `UserCard.svelte`
- Order within .svelte files:
  1. Script (imports, exports, logic)
  2. Markup (HTML)
  3. Style (CSS, scoped by default)

## State Management
- Use Svelte stores for global state
- Define stores in `src/lib/stores/`
- Use writable stores for mutable state
- Use derived stores for computed values
- Use readable stores for read-only state

## Data Fetching
- Use load functions for SSR data fetching
- Use SvelteKit's fetch for API calls
- Implement error handling in load functions
- Return properly typed data from load functions

## Forms and Mutations
- Use SvelteKit's form actions for mutations
- Progressive enhancement (works without JS)
- Handle validation errors in action responses
- Use enhance for client-side validation

## API Communication
- Create API client in `src/lib/utils/api.ts`
- Centralize API base URL
- Include authentication headers
- Handle errors consistently
- Use TypeScript interfaces for responses

## Component Patterns
```typescript
// src/lib/components/UserCard.svelte
<script lang="ts">
  import type { User } from '$lib/types';

  export let user: User;
  export let onEdit: (user: User) => void = () => {};

  function handleClick() {
    onEdit(user);
  }
</script>

<div class="card">
  <h3>{user.name}</h3>
  <p>{user.email}</p>
  <button on:click={handleClick}>Edit</button>
</div>

<style>
  .card {
    @apply border rounded p-4 shadow hover:shadow-lg;
  }
</style>
```

## Testing
- Use Vitest for unit tests
- Use Playwright for E2E tests
- Test components in isolation
- Mock API calls in tests
- Test accessibility
```

### 6.3 Development Workflow

**Step 1: Create API Client**

```
@agent Create an API client utility in src/lib/utils/api.ts

The client should:
- Use fetch API
- Include base URL from environment variables
- Add authentication headers (JWT token)
- Handle JSON responses
- Throw errors for failed requests
- Include TypeScript types for all methods

Create methods for:
- GET, POST, PUT, DELETE
- Specific methods for user operations (getUsers, createUser, etc.)

Reference: @docs/architecture/api-contracts.md for endpoint definitions
```

**Step 2: Create Shared Types**

```
@agent Create TypeScript interfaces for all API responses in src/lib/types/index.ts

Include types for:
- User, Role, Permission
- API responses (success, error, paginated)
- Form data structures

Export all types for use across the app
```

**Step 3: Build Components**

```
@agent Create a UserCard component in src/lib/components/UserCard.svelte

The component should:
- Display user name, email, role
- Show user avatar (or initials if no avatar)
- Include edit and delete action buttons
- Emit events for actions
- Use TailwindCSS for styling
- Be responsive (mobile-friendly)
- Follow accessibility best practices

Props:
- user: User
- onEdit: (user: User) => void
- onDelete: (user: User) => void
```

**Step 4: Create Routes with Data Loading**

```
@agent Create a users page in src/routes/users/+page.svelte with data loading in +page.ts

The page should:
- Load users from API in the load function
- Display users in a grid using UserCard components
- Include search functionality
- Implement pagination
- Show loading state
- Handle errors gracefully

+page.ts should:
- Fetch users from API using the api client
- Handle authentication
- Pass data to the page component
- Return proper types
```

**Step 5: Implement Forms with Actions**

```
@agent Create a user creation page in src/routes/users/create/+page.svelte with form action in +page.server.ts

The page should:
- Display a form for creating users
- Use SvelteKit form actions for submission
- Show validation errors
- Redirect on success
- Work without JavaScript (progressive enhancement)

+page.server.ts should:
- Define a 'create' form action
- Validate form data
- Call backend API to create user
- Return success or error responses
```

### 6.4 Hot Reload Configuration

**Ensure hot reload works properly:**

In `svelte.config.js`, ensure:

```javascript
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter()
  }
};

export default config;
```

**Auto-save in Cursor:**

Go to `Cursor Settings > Features > General` and enable:
- `Auto Save: onFocusChange`

This ensures files are saved when you switch context, triggering hot reload.

### 6.5 Live Preview with Cursor Browser

**Workflow for UI Development:**

1. **Split Screen Setup:**
   - Left: Code editor
   - Right: Cursor Browser

2. **Start Development Server:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Open in Browser:**
   ```
   @Browser Open http://localhost:5173
   ```

4. **Interactive Development:**
   ```
   Edit UserCard.svelte to change the card styling.
   
   @Browser Refresh and inspect the UserCard component. Suggest improvements for the hover effect and mobile responsiveness.
   ```

5. **Element-Specific Debugging:**
   ```
   @Browser Click on the "Edit" button in the first user card.
   
   Check:
   - Does the button work?
   - Are there any console errors?
   - What network requests are made?
   
   If there are issues, report them with the error message and stack trace.
   ```

6. **Automated UI Testing:**
   ```
   @Browser Test the user creation workflow:
   1. Navigate to /users/create
   2. Fill in the form with:
      - Name: John Doe
      - Email: john@example.com
      - Role: User
   3. Submit the form
   4. Verify the user appears in the user list
   
   Report any errors or UI issues.
   ```

### 6.6 Svelte Reactivity and Stores

**Create Global State Store:**

```
@agent Create a Svelte store for authentication in src/lib/stores/auth.ts

The store should:
- Hold current user and token
- Provide login and logout functions
- Persist token to localStorage
- Sync across tabs
- Export typed store and helper functions

Use Svelte's writable store pattern
```

**Use Store in Components:**

```
@agent Update the navigation component in src/lib/components/Nav.svelte to use the auth store

The component should:
- Show user name when authenticated
- Show login button when not authenticated
- Include logout button
- Use reactive statements ($:) to update UI
```

---

## 7. Phase 5: Integration & Testing

### 7.1 End-to-End Integration

**Create Integration Documentation:**

Create `docs/temp/integration-checklist.md`:

```markdown
# Integration Checklist

## Backend ↔ Admin
- [ ] Admin can authenticate with backend API
- [ ] Admin can fetch users from backend
- [ ] Admin can create users via backend API
- [ ] Admin can update users via backend API
- [ ] Admin can delete users via backend API
- [ ] API errors are handled gracefully in admin

## Backend ↔ Frontend
- [ ] Frontend can authenticate users
- [ ] Frontend can fetch and display users
- [ ] Frontend can create users
- [ ] Frontend can update users
- [ ] Frontend can delete users
- [ ] JWT tokens are refreshed properly

## Cross-Stack Features
- [ ] User created in admin appears in frontend
- [ ] User updated in frontend reflects in admin
- [ ] Pydantic-AI agents respond correctly to frontend queries
- [ ] All three components share consistent data models
```

### 7.2 Automated Integration Testing

**Use Parallel Agents for Multi-Stack Testing:**

1. **Open Cursor Composer** and enable parallel agents
2. **Create 3 Agent Sessions:**

**Agent 1 (Backend Test):**
```
@agent Run integration tests for the backend API.

Start the backend server, run pytest with coverage, and report results.

Command: cd backend && pytest tests/ -v --cov=src
```

**Agent 2 (Admin Test):**
```
@agent Run feature tests for the Laravel admin.

Start the admin server, run PHPUnit tests, and report results.

Command: cd admin && php artisan test
```

**Agent 3 (Frontend Test):**
```
@agent Run E2E tests for the Svelte frontend.

Start the frontend dev server, run Playwright tests, and report results.

Command: cd frontend && npm run test:e2e
```

3. **Compare Results:**
   - All three agents run in parallel
   - You get results from all stacks simultaneously
   - Identify integration issues quickly

### 7.3 Contract Testing

**Ensure API Contracts Are Followed:**

```
@agent Create contract tests that verify the backend API matches the documented contracts in docs/architecture/api-contracts.md

For each endpoint, test:
- Response status codes match documentation
- Response body schema matches documentation
- Error responses match documentation
- Authentication requirements match documentation

Use a contract testing library like Pact or Dredd
```

### 7.4 Cross-Stack Debugging with Browser

**Scenario: User creation works in admin but fails in frontend**

1. **Test in Admin:**
   ```
   @Browser Open http://localhost:8000/admin/users/create
   
   Create a user with:
   - Name: Test User
   - Email: test@test.com
   - Role: Admin
   
   Check network tab. What API request is made? What's the response?
   ```

2. **Test in Frontend:**
   ```
   @Browser Open http://localhost:5173/users/create
   
   Create a user with the same details.
   
   Check:
   - What API request is made?
   - Is the request format different from admin?
   - What's the error response?
   ```

3. **Compare and Fix:**
   ```
   @agent Compare the two API requests from admin and frontend.
   
   Differences found:
   - Admin sends: { "name": "Test User", ... }
   - Frontend sends: { "userName": "Test User", ... }
   
   Fix the frontend to use the correct field names per the API contract.
   ```

---

## 8. Phase 6: Debugging & Optimization

### 8.1 Console Debugging with Cursor Browser

**Automatic Console Log Capture:**

Cursor Browser automatically captures console logs, errors, and warnings.

**Example Workflow:**

```
@Browser Open the frontend at http://localhost:5173/dashboard

Check console logs. Are there any:
- JavaScript errors?
- Failed API requests?
- Warning messages?

Report all issues with full error messages and stack traces.
```

**Interactive Debugging:**

```
@Browser On the user list page, open the browser console.

Type: window.debugUser = true

Then trigger the user edit action. Report what happens in the console.
```

### 8.2 Network Request Debugging

**Monitor API Calls:**

```
@Browser Open http://localhost:5173/users and monitor network requests.

Filter by XHR/Fetch requests.

For the /api/v1/users request, check:
- Request headers (is auth token included?)
- Request payload
- Response status code
- Response body
- Response time

Report any anomalies or performance issues.
```

**Fix Slow Requests:**

```
The /api/v1/users request takes 3 seconds.

@agent Analyze the backend /api/v1/users endpoint for performance issues.

Check:
- Database queries (N+1 problems?)
- Missing indexes
- Unnecessary data loading
- Lack of caching

Suggest optimizations and implement the top 3 improvements.
```

### 8.3 Performance Profiling

**Backend Performance:**

```
@agent Profile the backend API endpoints and identify the slowest operations.

Use Python profiling tools (cProfile or py-spy) to:
- Identify slow database queries
- Find CPU-intensive operations
- Detect memory leaks
- Report the top 5 performance bottlenecks

Then optimize the worst offender.
```

**Frontend Performance:**

```
@Browser Use Lighthouse to audit the frontend at http://localhost:5173

Run performance, accessibility, and best practices audits.

Report:
- Performance score
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- Accessibility issues

Suggest and implement improvements to reach >90 performance score.
```

### 8.4 Error Tracking and Logging

**Implement Structured Logging:**

```
@agent Add structured logging to the backend using Python's logging module.

Configure:
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- JSON log formatting
- Log rotation
- Separate logs for API requests, agent operations, and errors

Example locations:
- API requests: logs/api.log
- Agent operations: logs/agents.log
- Errors: logs/errors.log
```

**Frontend Error Boundary:**

```
@agent Create a Svelte error boundary component that catches and logs errors.

The component should:
- Catch errors in child components
- Display a user-friendly error message
- Log errors to a logging service
- Allow users to retry or return home

Wrap the app in this error boundary in src/routes/+layout.svelte
```

### 8.5 Security Audit with Cursor Agent

**Run Security Checks:**

```
@agent Perform a security audit of the entire application.

Check for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- CSRF protection
- Authentication bypass
- Insecure data exposure
- Rate limiting on APIs
- Secrets in code or logs

Scan all three codebases (backend, admin, frontend) and report findings with severity levels (Critical, High, Medium, Low).

Fix all Critical and High severity issues.
```

---

## 9. Phase 7: Documentation & Code Review

### 9.1 Generate API Documentation

**OpenAPI/Swagger for Backend:**

```
@agent Generate OpenAPI 3.0 documentation for all backend API endpoints.

Include:
- Endpoint descriptions
- Request/response schemas
- Authentication requirements
- Example requests/responses
- Error responses

Save as backend/docs/openapi.yaml

Then generate HTML documentation using Redoc or Swagger UI.
```

**Auto-generate from Code:**

FastAPI includes automatic OpenAPI generation. Access at:
```
http://localhost:8000/docs
```

**Capture and Save:**

```
@Browser Open http://localhost:8000/docs

Export the OpenAPI JSON schema and save it to backend/docs/openapi.json
```

### 9.2 Generate Code Documentation

**Backend Docstrings:**

```
@agent Add comprehensive docstrings to all Python modules, classes, and functions in the backend.

Use Google-style docstrings:
- Description
- Args
- Returns
- Raises
- Examples

Then generate HTML documentation using Sphinx:
1. Install Sphinx
2. Create Sphinx config
3. Generate HTML docs
4. Save to backend/docs/html/
```

**Frontend JSDoc:**

```
@agent Add JSDoc comments to all TypeScript functions and components in the frontend.

Include:
- Function/component description
- Parameter types and descriptions
- Return type and description
- Usage examples

Then generate HTML documentation using TypeDoc.
```

### 9.3 Create User Documentation

**End-User Guide:**

```
@agent Create a user guide for the application in docs/user-guide.md

Include:
- Getting started
- Key features with screenshots (describe what they should look like)
- Step-by-step tutorials
- FAQs
- Troubleshooting

Use clear, non-technical language for end users.
```

### 9.4 Code Review with Cursor Agent

**Automated Code Review:**

Create `.cursor/commands/code-review.md`:

```markdown
# Code Review Command

Perform a comprehensive code review of the selected files or current changes.

Check for:
1. **Code Quality:**
   - Readability and clarity
   - DRY principle violations
   - Proper naming conventions
   - Code complexity (cyclomatic complexity)

2. **Best Practices:**
   - Language-specific best practices (PEP 8 for Python, PSR-12 for PHP, etc.)
   - Framework conventions (Django, Laravel, SvelteKit)
   - Design patterns usage

3. **Security:**
   - Input validation
   - SQL injection risks
   - XSS vulnerabilities
   - Authentication/authorization issues

4. **Performance:**
   - N+1 query problems
   - Unnecessary computations
   - Missing database indexes
   - Inefficient algorithms

5. **Testing:**
   - Test coverage
   - Edge cases covered
   - Mock usage
   - Test clarity

6. **Documentation:**
   - Docstrings/comments present
   - Clarity of comments
   - README updates needed

Provide:
- Summary of findings
- Severity levels (Critical, High, Medium, Low, Info)
- Specific line numbers and suggestions
- Code examples for improvements
```

**Run Code Review:**

Select files in the file explorer, then:

```
Type: /code-review
```

Cursor Agent will analyze the code and provide detailed feedback.

**Review PR Changes:**

```
@agent Review the git diff for the current branch against main.

git diff main...HEAD

Provide a code review focusing on:
- Breaking changes
- API contract changes
- Security issues
- Performance regressions

Format as a GitHub PR review with inline comments.
```

### 9.5 Generate Deployment Documentation

```
@agent Create deployment documentation in docs/deployment.md

Include:
1. Prerequisites (server requirements, dependencies)
2. Environment variables needed
3. Database setup and migrations
4. Backend deployment (Docker, systemd, or cloud)
5. Admin deployment (Apache/Nginx config)
6. Frontend deployment (static hosting, CDN)
7. Post-deployment checklist
8. Rollback procedures
9. Monitoring and logging setup

Provide specific commands and configuration examples.
```

---

## 10. Phase 8: Deployment

### 10.1 Containerization

**Create Dockerfiles:**

```
@agent Create Dockerfiles for all three services (backend, admin, frontend).

Backend Dockerfile:
- Use Python 3.11 slim image
- Install dependencies from requirements.txt
- Copy source code
- Expose port 8000
- Run with uvicorn

Admin Dockerfile:
- Use PHP 8.2-fpm image
- Install Composer dependencies
- Copy Laravel files
- Set up permissions
- Expose port 9000

Frontend Dockerfile:
- Use Node 20 image
- Install dependencies
- Build production bundle
- Use Nginx to serve static files
- Expose port 80

Optimize for small image size and security.
```

**Create docker-compose.yml:**

```
@agent Create a docker-compose.yml file in the project root.

Include services:
- postgres (database)
- redis (cache)
- backend (Python/FastAPI)
- admin (PHP/Laravel)
- frontend (SvelteKit/Nginx)

Configure:
- Networking between services
- Volume mounts for persistence
- Environment variables
- Health checks
- Restart policies

Add profiles for dev and production environments.
```

### 10.2 CI/CD Pipeline

**GitHub Actions Workflow:**

```
@agent Create a GitHub Actions workflow in .github/workflows/ci.yml

The workflow should:
1. Trigger on push to main and PRs
2. Run in parallel jobs:
   - Backend: lint, test, build
   - Admin: lint, test, build
   - Frontend: lint, test, build
3. Run integration tests
4. Build Docker images
5. Push images to registry
6. Deploy to staging (on main branch only)

Use matrix strategy for parallel execution.
Include caching for dependencies.
```

**Automated Code Review in CI:**

Create `.github/workflows/cursor-code-review.yml`:

```yaml
name: Cursor Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  code-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Install Cursor CLI
        run: |
          curl -fsSL https://cursor.sh/install.sh | sh
      
      - name: Perform Code Review
        env:
          CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
          GH_TOKEN: ${{ github.token }}
        run: |
          cursor-agent --force --model "claude-3-5-sonnet-20241022" \\
            --output-format=text --print "Review this PR and post inline comments"
```

### 10.3 Production Deployment

**Deploy to Cloud Provider:**

```
@agent Create deployment scripts for deploying to AWS/GCP/Azure.

Include:
1. Infrastructure as Code (Terraform or CloudFormation)
   - VPC and networking
   - Load balancers
   - Database (RDS/Cloud SQL)
   - Redis (ElastiCache/MemoryStore)
   - Container orchestration (ECS/Kubernetes/Cloud Run)
   
2. Deployment script (deploy.sh)
   - Build Docker images
   - Push to container registry
   - Update service definitions
   - Run database migrations
   - Health check verification
   - Rollback on failure

3. Environment configuration
   - Production environment variables
   - Secrets management (AWS Secrets Manager/Cloud KMS)
   - SSL/TLS certificates

Choose: [AWS/GCP/Azure] and provide specific implementation.
```

**Deployment Checklist:**

Create `docs/deployment-checklist.md`:

```markdown
# Production Deployment Checklist

## Pre-Deployment
- [ ] All tests passing in CI
- [ ] Code review completed
- [ ] Security audit performed
- [ ] Performance benchmarks met
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] Backup strategy in place

## Deployment Steps
- [ ] Tag release version in git
- [ ] Build production Docker images
- [ ] Push images to registry
- [ ] Update image tags in deployment config
- [ ] Run database migrations
- [ ] Deploy backend service
- [ ] Deploy admin service
- [ ] Deploy frontend service
- [ ] Verify health checks
- [ ] Run smoke tests

## Post-Deployment
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify all integrations working
- [ ] Test critical user flows
- [ ] Update documentation
- [ ] Notify team of deployment
- [ ] Monitor for 24 hours

## Rollback Procedure
- [ ] Keep previous image tags available
- [ ] Document rollback commands
- [ ] Test rollback in staging
- [ ] Have rollback plan ready
```

### 10.4 Monitoring and Observability

**Setup Application Monitoring:**

```
@agent Integrate application monitoring using Datadog/NewRelic/Prometheus.

Backend:
- Add instrumentation for FastAPI
- Track API response times
- Monitor agent operations
- Log errors to monitoring service

Admin:
- Integrate with Laravel monitoring
- Track page load times
- Monitor API calls to backend

Frontend:
- Add browser monitoring
- Track page navigation
- Monitor API calls
- Report JavaScript errors

Provide configuration and initialization code.
```

**Health Check Endpoints:**

```
@agent Add health check endpoints to all services.

Backend: GET /health
- Check database connection
- Check Redis connection
- Check Pydantic-AI model availability
- Return status: healthy/degraded/unhealthy

Admin: GET /health
- Check database connection
- Check backend API availability
- Return status and response time

Frontend: GET /health
- Simple static response
- Include build version

Implement in all three services.
```

---

## 11. Advanced Cursor 2.0 Features

### 11.1 Parallel Agents for Experimentation

**Use Case: Compare Different Implementations**

When you're unsure of the best approach, run parallel agents with different models:

1. Open Cursor Composer
2. Click the "Parallel Agents" icon (or configure in settings)
3. Configure agents:
   - Agent 1: Composer model
   - Agent 2: Claude 3.5 Sonnet
   - Agent 3: GPT-4

4. Run the same prompt on all three:

```
Refactor the user authentication flow to use JWT tokens instead of sessions.

Requirements:
- Generate and validate JWT tokens
- Include refresh token logic
- Update all endpoints to use JWT auth
- Maintain backward compatibility

Implement in backend/src/api/auth.py
```

5. Review outputs:
   - Each agent creates a separate git worktree
   - Compare implementations side-by-side
   - Pick the best approach or merge ideas
   - Use "Apply All" to merge selected agent's changes

### 11.2 Voice Mode for Rapid Prototyping

**Enable Voice Mode** and use natural language:

**Example Voice Commands:**

- "Create a dashboard component that shows user statistics with charts"
- "Refactor the database service to use connection pooling"
- "Add error handling to all API endpoints with proper status codes"
- "Generate unit tests for the user service with at least eighty percent coverage"
- "Update the frontend to use dark mode with a toggle switch"

**Best for:**
- Brainstorming features
- Quick prototypes
- Iterative refinement
- Hands-free code review

### 11.3 Team Commands and Shared Rules

**Create Team Commands in `.cursor/commands/`:**

**Example: `setup-feature.md`**

```markdown
# Setup New Feature Command

Create a new feature branch and scaffold all necessary files for a new feature.

Prompt the user for:
1. Feature name (e.g., "user-notifications")
2. Feature type (backend, admin, frontend, or full-stack)

Then:
1. Create feature branch: feature/[feature-name]
2. Based on type, create:
   - Backend: agent, service, API routes, tests
   - Admin: controller, views, routes, tests
   - Frontend: routes, components, stores, tests
   - Full-stack: all of the above
3. Update documentation:
   - Add feature to current-state.md
   - Create feature spec in docs/requirements/
4. Create initial commit

Follow all project conventions and rules.
```

**Usage:**

Type `/setup-feature` in Composer, and the agent will run the command.

**Share Across Team:**

Team commands can be:
- Committed to `.cursor/commands/` in git (all team members get them)
- Managed in Cursor Team Settings (centralized, no local files needed)

### 11.4 MCP Server Integration

**Use Case: Integrate with External Services**

Cursor 2.0 supports MCP (Model Context Protocol) for connecting to external services.

**Example: Integrate with Pydantic Logfire for Debugging**

1. Install Pydantic Logfire MCP:
   ```bash
   npm install -g @pydantic/logfire-mcp-server
   ```

2. Configure in `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "logfire": {
         "command": "logfire-mcp-server",
         "env": {
           "LOGFIRE_TOKEN": "${env:LOGFIRE_TOKEN}"
         }
       }
     }
   }
   ```

3. Use in Cursor Agent:
   ```
   @agent Check Pydantic Logfire for errors in the user-agent operations over the last hour.
   
   Analyze the logs and identify:
   - Most common errors
   - Performance bottlenecks
   - Failed agent operations
   
   Suggest fixes for the top 3 issues.
   ```

**Other MCP Integrations:**

- **GitHub MCP**: Query issues, create PRs, review code
- **Database MCP**: Query databases directly
- **Browser Tools MCP**: Advanced browser automation
- **Composio MCP**: Connect to 100+ SaaS tools

### 11.5 Cloud Agents and Background Tasks

**Use Case: Run Long-Running Tasks in the Cloud**

Cursor 2.0 supports cloud agents that run in remote environments.

**Configure Environment:**

Create `.cursor/environment.json`:

```json
{
  "baseImage": "ghcr.io/cursor-images/python-3.11:latest",
  "install": "pip install -r backend/requirements.txt",
  "start": "cd backend && uvicorn src.main:app --host 0.0.0.0",
  "terminals": [
    {
      "name": "backend",
      "command": "cd backend && uvicorn src.main:app --reload",
      "ports": [8000]
    },
    {
      "name": "frontend",
      "command": "cd frontend && npm run dev",
      "ports": [5173]
    }
  ],
  "env": {
    "DATABASE_URL": "${secret:DATABASE_URL}",
    "API_KEY": "${secret:API_KEY}"
  }
}
```

**Run Background Agent:**

```
@agent Create a background agent to refactor the entire user module.

Branch: feature/user-refactor

Tasks:
1. Extract business logic to services
2. Add comprehensive tests
3. Update API endpoints
4. Run all tests
5. Create PR when done

Run in cloud environment with full test suite.
```

The agent runs in a cloud VM, creates a branch, makes changes, runs tests, and opens a PR—all autonomously.

---

## 12. Best Practices & Pro Tips

### 12.1 Cursor Keyboard Shortcuts

Memorize these for maximum speed:

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Quick Edit (inline code changes) |
| `Cmd/Ctrl + I` | Open Composer (Agent mode) |
| `Cmd/Ctrl + L` | Open Chat (Ask mode) |
| `Cmd/Ctrl + Shift + L` | Clear Chat/Composer |
| `Cmd/Ctrl + /` | Add context (files, folders, docs) |
| `Cmd/Ctrl + Enter` | Accept suggestion |
| `Cmd/Ctrl + Backspace` | Reject suggestion |
| `Tab` | Accept inline completion |
| `Shift + Tab` | Switch between Plan/Agent modes |

### 12.2 Context Management

**Rules for Effective Context:**

1. **Less is More**: Only include relevant files
2. **Use @Symbols**:
   - `@Codebase`: Search entire project
   - `@Docs`: Reference documentation
   - `@Web`: Search the web
   - `@File`: Specific file
   - `@Folder`: Entire folder
3. **Reference Contracts**: Always include API contracts, schemas, and specs
4. **Keep Chat Focused**: Start new chat when changing context significantly

**Example of Good Context:**

```
@agent Create a user profile page

Context:
@docs/architecture/api-contracts.md (for API endpoints)
@frontend/src/lib/types/index.ts (for TypeScript types)
@frontend/src/lib/components/UserCard.svelte (for reference styling)

Requirements:
- Display user name, email, avatar, bio
- Include edit button (navigates to edit page)
- Show user's recent activity
- Use responsive design
```

### 12.3 Prompting Best Practices

**Effective Prompts Have:**

1. **Clear Goal**: What you want to achieve
2. **Context**: Relevant files and documentation
3. **Constraints**: Technologies, patterns, limits
4. **Example**: If applicable, show what you want
5. **Output Format**: Specify structure or format

**Bad Prompt:**

```
Create a user page
```

**Good Prompt:**

```
@agent Create a user profile page in frontend/src/routes/users/[id]/+page.svelte

Requirements:
- Load user data in +page.ts using the API client
- Display: name, email, avatar, bio, join date
- Include "Edit Profile" button (only if current user)
- Show user's recent posts (3 most recent)
- Handle loading and error states
- Mobile-responsive design with TailwindCSS

Reference:
@docs/architecture/api-contracts.md (GET /api/v1/users/{id})
@frontend/src/lib/components/UserCard.svelte (for styling consistency)
```

### 12.4 When to Use Each Mode

| Mode | Use When | Example |
|------|----------|---------|
| **Ask Mode** | Understanding code, getting explanations | "How does this auth middleware work?" |
| **Agent Mode** | Building features, refactoring, multi-file changes | "Add user authentication to the app" |
| **Edit Mode** | Small, precise changes to selected code | "Change this function to use async/await" |
| **Plan Mode** | Architecting complex features, breaking down work | "Plan the implementation of a notification system" |
| **Browser Mode** | Testing, debugging UI, visual verification | "Test the user signup flow" |
| **Voice Mode** | Rapid prototyping, hands-free coding | "Add a dark mode toggle to the navigation" |

### 12.5 Iterative Development Loop

**The "Build-Test-Fix" Cycle:**

1. **Build**: Use Agent mode to generate code
2. **Test**: Use Browser mode or run automated tests
3. **Fix**: Use Edit mode for small fixes or Agent mode for larger changes
4. **Repeat**: Until tests pass and feature is complete

**Example:**

```
# Build
@agent Create a user login form in frontend/src/routes/login/+page.svelte

# Test (let Cursor run the test)
@agent Run the frontend dev server and open in browser. Test the login form with these credentials:
- Email: test@example.com
- Password: password123

Report any issues.

# Fix (based on test results)
@agent The login form doesn't show validation errors. Update to display field errors returned from the API.

# Test again
@agent Test the login form again with invalid credentials. Verify errors are shown.
```

### 12.6 Managing Large Codebases

**Strategies for Large Projects:**

1. **Use `.cursorignore`**: Exclude unnecessary files
   ```
   node_modules/
   .venv/
   __pycache__/
   .git/
   *.log
   dist/
   build/
   coverage/
   ```

2. **Split Rules by Domain**: Use `.cursor/rules/` with multiple .mdc files
   - `backend.mdc`
   - `admin.mdc`
   - `frontend.mdc`
   - `testing.mdc`

3. **Maintain Documentation**: Keep `docs/temp/current-state.md` updated
   ```
   @agent Update docs/temp/current-state.md with:
   - Features completed today
   - Current blockers
   - Next priorities
   ```

4. **Use Commands**: Create reusable commands for common workflows
   - `/run-all-tests`
   - `/code-review`
   - `/generate-docs`

5. **Scope Agents**: When creating agents, specify folders
   ```
   @agent [scope: backend/] Create a new Pydantic-AI agent for content moderation
   ```

### 12.7 Collaboration with Cursor

**Team Workflows:**

1. **Share Rules**: Commit `.cursorrules` and `.cursor/rules/` to git
2. **Share Commands**: Commit `.cursor/commands/` to git
3. **Document Decisions**: Keep `docs/temp/decisions.md` updated
4. **Review PRs**: Use `/code-review` command on PR diffs
5. **Onboard Quickly**: New team members inherit all rules and commands

**Team Settings (Cursor Teams Feature):**

If your team has Cursor Teams, you can:
- Centrally manage rules (no local files needed)
- Share commands across the organization
- Control model access and usage
- Track team usage and costs

### 12.8 Security Considerations

**Important Security Practices:**

1. **Never Commit Secrets**:
   - Use `.env` files (add to `.gitignore`)
   - Use environment variables
   - Use secret management services

2. **Review AI-Generated Code**:
   - Always review before committing
   - AI can make security mistakes
   - Use `/code-review` for security audit

3. **Disable YOLO Mode for Production**:
   - Only enable for experimental work
   - Always review commands before execution in prod

4. **Sanitize Context**:
   - Don't include sensitive data in prompts
   - Be careful with API keys in chat history

5. **Use Sandboxed Terminals**:
   - Enable sandboxed terminals in settings
   - Prevents accidental destructive commands

### 12.9 Performance Tips

**Speed Up Development:**

1. **Enable Auto-Save**: Files save automatically, triggering hot reload
2. **Use Composer Model**: 4x faster than Claude/GPT for coding tasks
3. **Cache Dependencies**: Use Docker layer caching, npm cache
4. **Use Parallel Agents**: Run multiple agents simultaneously for different tasks
5. **Preload Context**: Add common files to chat before starting work

**Speed Up Cursor Itself:**

- Close unused workspace folders
- Exclude large directories in `.cursorignore`
- Use "Index Codebase" selectively (disable for very large repos)
- Clear chat history periodically

### 12.10 Troubleshooting Common Issues

**Problem: Agent generates incorrect code**

**Solution:**
- Add more specific context and constraints
- Reference exact documentation with `@Docs`
- Provide examples of what you want
- Use stricter rules in `.cursorrules`

**Problem: Hot reload not working**

**Solution:**
- Enable auto-save in Cursor settings
- Check dev server is running
- Restart dev server
- Check for syntax errors preventing reload

**Problem: Browser feature not working**

**Solution:**
- Ensure you're on Cursor 2.0+
- Enable Browser in Beta settings
- Restart Cursor
- Check if port is accessible

**Problem: Tests failing in CI but passing locally**

**Solution:**
- Check environment differences
- Mock external dependencies in tests
- Use consistent test data
- Run tests in Docker locally to match CI

**Problem: Parallel agents create conflicts**

**Solution:**
- Ensure agents work on different files
- Review merge carefully
- Use separate branches for each agent
- Merge one at a time

---

## Conclusion

This comprehensive guide provides a complete software development lifecycle workflow using Cursor 2.0 for your multi-stack application (Pydantic-AI backend, Laravel admin, Svelte frontend). 

**Key Takeaways:**

1. **Structure Matters**: Organize your monorepo clearly with proper rules and documentation
2. **Use Agent Mode**: Leverage Composer model for 4x faster code generation
3. **Browser Integration**: Test and debug visually with the built-in browser
4. **Parallel Agents**: Experiment with different approaches simultaneously
5. **Iterative Development**: Build, test, fix in tight loops
6. **Document Everything**: Keep contracts, specs, and current state documented
7. **Automate Testing**: Use agents to run tests and fix failures autonomously
8. **Review and Refine**: Use code review commands before committing
9. **Deploy Confidently**: Use checklists and automation for safe deployments
10. **Iterate and Improve**: Continuously refine your workflow and rules

By following this guide and leveraging Cursor 2.0's revolutionary features, you can **dramatically accelerate your development speed** while maintaining high code quality and comprehensive test coverage.

**Next Steps:**

1. Set up your project structure following Section 2
2. Configure Cursor 2.0 with global and project-specific rules
3. Start with Phase 1 (Planning) to establish solid foundations
4. Progress through each development phase systematically
5. Iterate and refine your workflow based on what works best for your team

Happy coding! 🚀
