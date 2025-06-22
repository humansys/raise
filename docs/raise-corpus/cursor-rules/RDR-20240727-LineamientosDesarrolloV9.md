# Rules Decision Record (RDR) - Lineamientos Desarrollo Web-Mobile v9

*   **Source Document:** `Lineamientos Desarrollo Web-Mobile v9.docx.pdf.md`
*   **Target Repository:** `raise-roome-poc`
*   **Start Time:** 2024-07-27
*   **Agent:** Gemini (SAR Agent Role)

## Log Entries

*(Entries will be added below as rules are processed)*

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 56, Section "Guía de Nomenclatura..."
*   **RuleSummary:** File Naming: Components/Classes/Types/Interfaces use PascalCase.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** The convention is already present in the foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** File Naming: Functions/Hooks use camelCase.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** File Naming: Component directories use PascalCase.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** File Naming: Utility directories use camelCase/lowercase.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `001-core-setup.mdc` (Enhancement)
*   **SourceLocation:** Lineamientos_v9.md, p. 56-57
*   **RuleSummary:** File Naming: Use meaningful suffixes.
*   **Decision:** Approved (Enhance existing rule `001-core-setup.mdc`).
*   **Details:** Added specific suffixes from source doc: `.constants.ts`, `.helpers.ts`, `.screen.tsx`, `.actions.ts`, `.reducers.ts`, `.sagas.ts`, `.selectors.ts`, `.mocks.ts`, `.models.ts`, `.stories.tsx`.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** File Naming: Use index.ts/index.tsx for barrel exports.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `001-core-setup.mdc` (Enhancement)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** Code Naming: Variables/Functions/Hooks use camelCase.
*   **Decision:** Approved (Enhance existing rule `001-core-setup.mdc`).
*   **Details:** Added explicit rule for code element naming (camelCase).
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `001-core-setup.mdc` (Enhancement)
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** Code Naming: Components/Classes use PascalCase.
*   **Decision:** Approved (Enhance existing rule `001-core-setup.mdc`).
*   **Details:** Added explicit rule for code element naming (PascalCase).
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A
*   **SourceLocation:** Lineamientos_v9.md, p. 56
*   **RuleSummary:** Code Naming: snake_case for Config/DB.
*   **Decision:** Rejected (Not applicable to TS/React frontend scope).
*   **Details:** Convention relates to configuration or database naming, not typical frontend code generation.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`, `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Naming: Interfaces use `i` prefix.
*   **Decision:** Approved (Covered by existing rules `100-typescript.mdc`, `200-react-next.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Naming: Types use PascalCase.
*   **Decision:** Approved (Covered by existing rule `100-typescript.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 60, Section "Guía de Estandarización..."
*   **RuleSummary:** Prefer named exports, avoid default/wildcard imports.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** The convention is already present and enforced in the foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A
*   **SourceLocation:** Lineamientos_v9.md, p. 60
*   **RuleSummary:** Use wildcard imports only if > 15 lines.
*   **Decision:** Rejected.
*   **Details:** Conflicts with the stricter foundational rule `001-core-setup.mdc` which strongly avoids wildcard imports. The 15-line condition is also difficult to enforce consistently via AI. Prioritizing the simpler, stricter existing rule.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`, `300-nx-monorepo.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 62
*   **RuleSummary:** Use path aliases for imports.
*   **Decision:** Approved (Covered by existing rules `001-core-setup.mdc`, `300-nx-monorepo.mdc`).
*   **Details:** Convention is well-established in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `001-core-setup.mdc` (Enhancement)
*   **SourceLocation:** Lineamientos_v9.md, p. 60-62
*   **RuleSummary:** Use barrel files (`index.ts`) for centralizing exports in common directories.
*   **Decision:** Approved (Enhance existing rule `001-core-setup.mdc`).
*   **Details:** Added clarification on using barrel files for directories like `constants`, `components`, `hooks`, `utils` within the Import Structure section.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Group/order imports logically.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Convention already present in foundational rules.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Avoid using `any` type.
*   **Decision:** Approved (Covered by existing rule `100-typescript.mdc`).
*   **Details:** Foundational rule already enforces this best practice.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Use `interface` for defining object shapes.
*   **Decision:** Approved (Covered by existing rule `100-typescript.mdc`).
*   **Details:** Foundational rule establishes this convention.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Use `type` for utility types, unions, intersections, aliases.
*   **Decision:** Approved (Covered by existing rule `100-typescript.mdc`).
*   **Details:** Foundational rule establishes this convention.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `100-typescript.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Prefer string enums over numeric enums.
*   **Decision:** Approved (Covered by existing rule `100-typescript.mdc`).
*   **Details:** Foundational rule establishes this best practice.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Use Functional Components with Hooks.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Use `i` prefix for prop interfaces.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Use prop destructuring.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Custom Hook conventions (use*, hooks/, i-prefix IO).
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Adhere to Rules of Hooks.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 18-20
*   **RuleSummary:** State Management: Use Redux Toolkit (useSelector, useDispatch, typed patterns).
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule covers the actionable coding patterns.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Local State: Use useState.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 37-38
*   **RuleSummary:** Use Next.js App Router conventions.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule aligns with source document mandate.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 38 (implicit)
*   **RuleSummary:** Data Fetching: Prefer Redux thunks (Server) or useEffect (Client).
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule provides specific preference.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 38 (implicit)
*   **RuleSummary:** Use `'use client'` directive correctly; keep Client Components minimal.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule provides specific guidance.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `200-react-next.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Accessibility (a11y) best practices.
*   **Decision:** Approved (Covered by existing rule `200-react-next.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `200-react-next.mdc` (Enhancement)
*   **SourceLocation:** Lineamientos_v9.md, p. 53-54
*   **RuleSummary:** Use Error Boundaries for handling render errors, preferably `react-error-boundary`.
*   **Decision:** Approved (Enhance existing rule `200-react-next.mdc`).
*   **Details:** Added section on Error Handling recommending `react-error-boundary` for functional components, aligning with source doc and functional component preference.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `400-styling.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 45 / Foundational `400-styling`
*   **RuleSummary:** Styling: Use dedicated `*.styled.tsx` files.
*   **Decision:** Approved (Covered by existing rule `400-styling.mdc`).
*   **Details:** Foundational rule establishes this file structure.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `400-styling.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Styling: Use PascalCase for styled component names.
*   **Decision:** Approved (Covered by existing rule `400-styling.mdc`).
*   **Details:** Foundational rule establishes this naming convention.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `400-styling.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Styling: Use transient props (`$`) for styling-only props.
*   **Decision:** Approved (Covered by existing rule `400-styling.mdc`).
*   **Details:** Foundational rule establishes this convention.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `400-styling.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Styling: Type styled component props using interfaces (`i` prefix).
*   **Decision:** Approved (Covered by existing rule `400-styling.mdc`).
*   **Details:** Foundational rule establishes this convention.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `400-styling.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 45 / Foundational `400-styling`
*   **RuleSummary:** Styling: Use theme variables instead of hardcoding values.
*   **Decision:** Approved (Covered by existing rule `400-styling.mdc`).
*   **Details:** Foundational rule establishes this best practice.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 64
*   **RuleSummary:** Testing: Follow specific import order in test files.
*   **Decision:** Approved (Create new rule file `500-testing.mdc`).
*   **Details:** Established specific import order (React, Libs A-Z, Aliases A-Z, Relative A-Z, Styles A-Z) for test files.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 64-65
*   **RuleSummary:** Testing: Follow standard test file structure (mocks, setup/teardown, describe/it).
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Defined standard layout for test file elements.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 65
*   **RuleSummary:** Testing: Use appropriate RTL queries (getBy, findBy, waitFor).
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Specified usage context for different RTL query types.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 65
*   **RuleSummary:** Testing: Use `fireEvent` or `user-event` for interactions.
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Included recommendation for simulating user events.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 66
*   **RuleSummary:** Testing: Use `waitFor` for asynchronous updates/assertions.
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Included guidance on handling async operations.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 66
*   **RuleSummary:** Testing: Co-locate test files (`*.test.tsx`) or use `__tests__` directory.
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Defined conventions for test file location and naming.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/500-testing.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 67
*   **RuleSummary:** Testing: Mock child components and external dependencies for isolation.
*   **Decision:** Approved (Add to new rule file `500-testing.mdc`).
*   **Details:** Included recommendation for mocking.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `300-nx-monorepo.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 5, 29-30 / Foundational `300-nx-monorepo`
*   **RuleSummary:** Monorepo: Enforce strict boundaries between apps; use shared libs.
*   **Decision:** Approved (Covered by existing rule `300-nx-monorepo.mdc`).
*   **Details:** Foundational rule already enforces this core principle.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `300-nx-monorepo.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 62 / Foundational `300-nx-monorepo`
*   **RuleSummary:** Monorepo: Always use path aliases for library imports.
*   **Decision:** Approved (Covered by existing rule `300-nx-monorepo.mdc`).
*   **Details:** Foundational rule already enforces this.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** Lineamientos_v9.md, p. 47-48 / Foundational `001-core-setup`
*   **RuleSummary:** Enforce ESLint and Prettier usage.
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Foundational rule mandates usage and addressing errors/warnings.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A
*   **SourceLocation:** Lineamientos_v9.md, p. 44-45
*   **RuleSummary:** Use React Query for specific caching strategy.
*   **Decision:** Rejected (Not suitable for `.mdc` rule).
*   **Details:** Describes a specific architectural pattern, not easily enforceable as a general coding rule via AI. Potential conflict with other principles mentioned.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** `.cursor/rules/600-internationalization.mdc` (New)
*   **SourceLocation:** Lineamientos_v9.md, p. 46-47
*   **RuleSummary:** Use i18next for handling all user-facing text.
*   **Decision:** Approved (Create new rule file `600-internationalization.mdc`).
*   **Details:** Mandates using i18next functions/components for internationalization.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27

---

*   **RuleID/Filename:** N/A (Covered by `001-core-setup.mdc`)
*   **SourceLocation:** N/A (From foundational rules)
*   **RuleSummary:** Commenting best practices (Why not What, TODOs, no commented code).
*   **Decision:** Approved (Covered by existing rule `001-core-setup.mdc`).
*   **Details:** Foundational rule already enforces these commenting guidelines.
*   **Resolver:** Agent/HITL
*   **Timestamp:** 2024-07-27 