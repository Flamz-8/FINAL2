---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Constitution Compliance**: This template enforces Test-First Development (Constitution Principle II). Tests MUST be written and approved before implementation. Each user story phase follows Red-Green-Refactor workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

**Constitution Workflow**: RED → GREEN → REFACTOR (Tests first, then implementation, then optimization)

### Tests for User Story 1 (REQUIRED - Write First)

> **⚠️ CRITICAL - TEST-FIRST DEVELOPMENT**: 
> 1. Write these tests FIRST based on spec.md acceptance criteria
> 2. Get user/stakeholder approval of test scenarios
> 3. Run tests - they MUST FAIL (RED phase)
> 4. Only then proceed to implementation tasks below
> 5. Implementation makes tests pass (GREEN phase)
> 6. Refactor for code quality while keeping tests green

- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
  - Verify API contract, request/response schemas, error codes
  - Ensures public interface doesn't break
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py
  - Test complete user flow from acceptance scenarios
  - Multi-component interaction validation

**Checkpoint - RED Phase**: Tests written, approved, and failing ❌

### Implementation for User Story 1 (Make Tests Pass)

- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py
  - Include type annotations for all fields (Code Quality: Type Safety)
  - Single responsibility - one entity per file
- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py
  - Include type annotations for all fields (Code Quality: Type Safety)
- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)
  - Single responsibility - focused business logic
  - All error paths explicitly handled with context
- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py
  - Type-safe request/response handling
  - User-facing error messages are actionable
- [ ] T016 [US1] Add validation and error handling
  - No silent failures - all errors logged and handled
- [ ] T017 [US1] Add logging for user story 1 operations
  - Structured logging for debugging

**Checkpoint - GREEN Phase**: All tests passing ✅

### Code Quality & Refactor for User Story 1

- [ ] T018 [US1] Code review prep: Verify single responsibility, type safety, DRY principles
- [ ] T019 [US1] Performance check: Verify latency targets met, no N+1 queries
- [ ] T020 [US1] Refactor: Extract duplicated logic, improve readability
- [ ] T021 [US1] Documentation: Update API docs, add inline comments for "why"

**Checkpoint - User Story 1 Complete**: Tests green, code quality verified, ready for review ✅

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

**Constitution Workflow**: RED → GREEN → REFACTOR (Tests first, then implementation, then optimization)

### Tests for User Story 2 (REQUIRED - Write First)

> **⚠️ TEST-FIRST DEVELOPMENT**: Tests → Approval → Fail → Implement → Pass → Refactor

- [ ] T022 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T023 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

**Checkpoint - RED Phase**: Tests written, approved, and failing ❌

### Implementation for User Story 2 (Make Tests Pass)

- [ ] T024 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T025 [US2] Implement [Service] in src/services/[service].py
- [ ] T026 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T027 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint - GREEN Phase**: All tests passing ✅

### Code Quality & Refactor for User Story 2

- [ ] T028 [US2] Code review prep and quality verification
- [ ] T029 [US2] Performance validation
- [ ] T030 [US2] Refactor and documentation

**Checkpoint - User Story 2 Complete**: Tests green, code quality verified ✅

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

**Constitution Workflow**: RED → GREEN → REFACTOR

### Tests for User Story 3 (REQUIRED - Write First)

- [ ] T031 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T032 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

**Checkpoint - RED Phase**: Tests written, approved, and failing ❌

### Implementation for User Story 3 (Make Tests Pass)

- [ ] T033 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T034 [US3] Implement [Service] in src/services/[service].py
- [ ] T035 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint - GREEN Phase**: All tests passing ✅

### Code Quality & Refactor for User Story 3

- [ ] T036 [US3] Code review prep and quality verification
- [ ] T037 [US3] Performance validation
- [ ] T038 [US3] Refactor and documentation

**Checkpoint - All User Stories Complete**: All tests green, quality verified ✅

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories or ensure overall quality

**Constitution Gates**: Verify all quality, testing, UX, and performance requirements are met

- [ ] TXXX [P] Documentation updates in docs/
  - API documentation complete with examples
  - User guides updated
  - Architecture notes reflect current design
- [ ] TXXX Code cleanup and refactoring
  - DRY violations addressed (3+ duplications refactored)
  - Single responsibility verified across codebase
  - Type annotations complete for all public APIs
- [ ] TXXX Performance optimization across all stories
  - Latency targets verified (< 100ms interactions, < 200ms p95 APIs)
  - N+1 query problems eliminated
  - Resource constraints validated (memory bounds, no blocking operations)
- [ ] TXXX [P] Additional unit tests (if needed to meet coverage targets)
  - Overall coverage ≥ 80%
  - Business logic coverage ≥ 90%
  - Critical paths coverage = 100%
- [ ] TXXX Security hardening
  - Dependency vulnerability scan passed
  - Error messages don't leak sensitive data
  - Input validation on all user-facing inputs
- [ ] TXXX Accessibility audit (for user-facing features)
  - WCAG 2.1 Level AA compliance verified
  - Keyboard navigation tested
  - Screen reader compatibility confirmed
- [ ] TXXX Performance monitoring setup
  - Instrumentation on all endpoints
  - Alerts configured for regressions
  - Performance budgets in CI/CD
- [ ] TXXX Run quickstart.md validation

**Final Quality Gate**: All constitution principles verified before deployment ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story (Constitution Enforcement)

**Test-First Development (Mandatory)**:
1. **RED Phase**: Write tests based on acceptance criteria → Get approval → Tests FAIL
2. **GREEN Phase**: Implementation to make tests pass
3. **REFACTOR Phase**: Code quality improvements while keeping tests green

**Code Quality Standards**:
- Tests → Models → Services → Endpoints → Integration
- Type annotations before implementation
- Error handling explicit in all code paths
- Single responsibility verified during refactor

**Coverage Requirements**:
- Contract tests for all public APIs (100% coverage)
- Integration tests for all user journeys (per acceptance criteria)
- Overall coverage targets met (80% minimum)

**Quality Gates**:
- Code review approval required
- Performance targets verified
- No linting or type-checking errors

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
