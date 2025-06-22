# Rule Candidates from Lineamientos Desarrollo Web-Mobile v9

This document lists potential rules identified from `Lineamientos Desarrollo Web-Mobile v9.docx.pdf.md` to be converted into `.mdc` format for the `raise-roome-poc` repository using the SAR Agent process.

## Candidate List

*(Checklist: [ ] To Do, [X] Done)*

**1. Naming Conventions (From "Guía de Nomenclatura...")**
    *   [ ] **Files - Components/Classes/Types/Interfaces:** PascalCase (e.g., `MyComponent.tsx`, `UserData.ts`, `iNavbarProps.ts`). (Ref: p. 56 / Line 1714)
    *   [ ] **Files - Functions/Hooks:** camelCase (e.g., `useDataFetcher.ts`, `calculateTotal.ts`). (Ref: p. 56 / Line 1714)
    *   [ ] **Files - Directories (Components):** PascalCase (e.g., `src/components/UserProfile/`). (Ref: p. 56 / Line 1714) - *Note: May be better as a general guideline than a strict rule.*
    *   [ ] **Files - Directories (Utils/Hooks):** camelCase or lowercase (e.g., `src/utils/`, `src/hooks/`). (Ref: p. 56 / Line 1714) - *Note: May be better as a general guideline.*
    *   [ ] **Files - Suffixes:** Use meaningful suffixes (`.spec.ts`, `.test.tsx`, `.styled.ts`, `.utils.ts`, `.constants.ts`, `.helpers.ts`, `.screen.tsx`, `.actions.ts`, `.reducers.ts`, `.sagas.ts`, `.selectors.ts`, `.mocks.ts`, `.models.ts`, `.stories.tsx`). (Ref: p. 56-57 / Lines 1714, 1730-1768) - *Note: Could be multiple rules or one combined rule.*
    *   [ ] **Files - Index Files:** Use `index.ts` or `index.tsx` for barrel exports. (Ref: p. 56 / Line 1714)
    *   [ ] **Code - Variables/Functions/Hooks:** camelCase. (Ref: p. 56 / Line 1708)
    *   [ ] **Code - Components/Classes:** PascalCase. (Ref: p. 56 / Line 1711)
    *   [ ] **Code - Config/DB (if applicable):** snake_case (Mentioned but maybe less relevant for Cursor rules). (Ref: p. 56 / Line 1714)
    *   [ ] **Interfaces (TypeScript):** Prefix with `i` (e.g., `iUserProfile`). (Ref: Foundational `100-typescript` rule, cross-reference if mentioned in source). *Self-Correction: The document doesn't explicitly state `i` prefix in the Naming section, but it IS required by the foundational rules (Rule 100-typescript, 200-react-next). We should create/enforce this based on the foundational rules.*
    *   [ ] **Types (TypeScript):** PascalCase (e.g., `UserId`). (Ref: Foundational `100-typescript` rule).

**2. Import/Export Structure (From "Guía de Estandarización...")**
    *   [ ] **Prefer Named Exports:** Avoid default exports unless necessary; strongly avoid wildcard (`*`) imports. (Ref: p. 60 / Line 1810)
    *   [ ] **Limit Wildcard Imports:** Use `import * as Name` only if imports exceed 15 lines. (Ref: p. 60 / Line 1815) - *Note: This is quite specific, might be hard to enforce automatically.*
    *   [ ] **Use Path Aliases:** Utilize configured path aliases (`@components`, etc.) instead of relative paths. (Ref: p. 62 / Line 1878, also foundational rule `300-nx-monorepo`)
    *   [ ] **Barrel Files (`index.ts`):** Use index files to centralize exports within directories (`constants`, `components`, `hooks`, `utils`). (Ref: p. 60-62 / Lines 1826, 1840, 1857, 1871)
    *   [ ] **Grouping/Ordering:** Group imports (React, external, internal, relative). (Ref: Foundational `001-core-setup` rule, check if mentioned in source). *Self-Correction: Source doc doesn't explicitly mention order, rely on foundational rules.*

**3. TypeScript Best Practices**
    *   [ ] **Avoid `any`:** Explicitly disallow `any`; use `unknown` for catch blocks, specific types otherwise. (Ref: Foundational `100-typescript` rule, check source). *Self-Correction: Source doc doesn't seem to explicitly forbid `any`, rely on foundational rule.*
    *   [ ] **Use `interface` for Object Shapes:** Define props, API responses with `interface`. (Ref: Foundational `100-typescript` rule, check source).
    *   [ ] **Use `type` for Unions/Intersections/Aliases:** Use `type` for utility types, unions, etc. (Ref: Foundational `100-typescript` rule, check source).
    *   [ ] **Prefer String Enums:** Use string enums over numeric ones. (Ref: Foundational `100-typescript` rule, check source).

**4. React/Next.js Conventions**
    *   [ ] **Functional Components:** Always use functional components with hooks. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Props Interface Naming:** Use `interface` prefixed with `i` for props (e.g., `iMyComponentProps`). (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Props Destructuring:** Use object destructuring for props in function signature. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Custom Hooks:** Encapsulate logic in custom hooks (`use*`), place in `hooks/`, define IO interfaces with `i` prefix. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Adhere to Rules of Hooks:** Call hooks only at top level and from React functions. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **State Management (Redux Toolkit):** Use `useSelector` with `iRootState`, `useDispatch` with `AppDispatch`. Follow slice/thunk patterns. Ensure typing (no `any`). (Ref: p. 18-20 / Lines 549-618, also foundational rule `200-react-next`).
    *   [ ] **Local State:** Use `useState` for component-local state. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Next.js App Router:** Use App Router conventions (`app/`, `page.tsx`, `layout.tsx`). (Ref: p. 37-38 / Lines 1124-1172).
    *   [ ] **Data Fetching (Next.js):** Prefer fetching in Redux thunks (Server Components) or `useEffect` (Client Components). (Ref: p. 38 / Line 1161, also foundational `200-react-next`).
    *   [ ] **Client Components (`'use client'`):** Use directive for components with hooks; keep them minimal. (Ref: p. 38 / Line 1161, also foundational `200-react-next`).
    *   [ ] **Accessibility (a11y):** Use semantic HTML, ARIA attributes, alt text, form labels. (Ref: Foundational `200-react-next` rule, check source).
    *   [ ] **Error Handling (Error Boundaries):** Use `react-error-boundary` for functional components or class components with `componentDidCatch`/`getDerivedStateFromError`. (Ref: p. 53-54 / Lines 1620-1678).

**5. Styling (Styled Components)**
    *   [ ] **Dedicated Files:** Define styles in `*.styled.tsx` co-located with the component. (Ref: p. 45 / Line 1387, also foundational `400-styling`).
    *   [ ] **Naming:** Use PascalCase for styled components. (Ref: Foundational `400-styling` rule, check source).
    *   [ ] **Transient Props:** Prefix styling-only props with `$`. (Ref: Foundational `400-styling` rule, check source).
    *   [ ] **Typing Props:** Define interfaces (prefixed with `i`) for styled component props. (Ref: Foundational `400-styling` rule, check source).
    *   [ ] **Use Theme Variables:** Leverage theme variables (`colorsFlatMap`, spacing, fonts) instead of hardcoding. (Ref: Foundational `400-styling` rule, check source).

**6. Testing (Jest + RTL)**
    *   [ ] **Import Order:** Follow specific import order (React, libs A-Z, aliases A-Z, relative A-Z, styles A-Z). (Ref: p. 64 / Lines 1939-1953).
    *   [ ] **Test Structure:** Mocks/globals first, `beforeEach`, `afterEach`, `describe`/`it`. (Ref: p. 64-65 / Lines 1958-1974).
    *   [ ] **Queries:** Use `getBy`, `findBy`, `waitFor` appropriately. (Ref: p. 65 / Lines 1978-1983).
    *   [ ] **Interactions:** Use `fireEvent` or `userEvent`. (Ref: p. 65 / Lines 1985-1988).
    *   [ ] **Async:** Use `waitFor` for async updates. (Ref: p. 66 / Lines 1990-1993).
    *   [ ] **File Location:** Place tests in `__tests__` or co-located with `.test.tsx` suffix. (Ref: p. 66 / Lines 1999-2006).
    *   [ ] **Mocking:** Mock child components or external dependencies. (Ref: p. 67 / Lines 2016-2019).

**7. Monorepo Structure (Nx)**
    *   [ ] **Strict Boundaries:** Apps cannot import directly from other apps. Use shared libs. (Ref: Foundational `300-nx-monorepo` rule, check source p. 5, 29-30 / Lines 135, 895-943).
    *   [ ] **Path Aliases:** Always use aliases (`@components`, `@helpers`, etc.) for lib imports. (Ref: Foundational `300-nx-monorepo` rule, check source p. 62 / Line 1878).

**8. Other Tools & Practices**
    *   [ ] **ESLint/Prettier:** Enforce usage (Implied by document sections, Ref: p. 47-48 / Lines 1438-1479, also foundational `001-core-setup`). - *Note: Rule might be "Code must pass configured ESLint/Prettier checks".*
    *   [ ] **React Query:** Use for caching data with low update frequency (cache time configurable > 1 min). (Ref: p. 44-45 / Lines 1333-1378). - *Note: This describes usage, maybe less of a strict *code* rule.*
    *   [ ] **i18next:** Use for internationalization. (Ref: p. 46-47 / Lines 1399-1436). - *Note: Usage pattern rule, e.g., "Use i18next hooks/components for all user-facing text".*
    *   [ ] **Comments:** Explain "Why", not "What"; use `// TODO:`; remove commented code. (Ref: Foundational `001-core-setup` rule, check source).

**Sections Less Likely to Yield Direct Code Rules:**

*   Arquitectura Front End / Principios Clave (p. 4-5): High-level goals, not specific code rules.
*   Storybook configuration/strategies (p. 7-17): Tool setup and workflow.
*   Redux Toolkit Thunk Justification (p. 18-20): Explains *why*, but the actionable part is covered in State Management.
*   React Native CLI Justification (p. 21-22): Tool choice justification.
*   GitFlow (p. 23-25): Process guideline.
*   Deployment (Fastlane/Bitrise/Jenkins) (p. 26-27): Process guideline.
*   Ambientes (PROD/LAB/QA) (p. 28): Environment setup.
*   Nx Justification (p. 29-31): Tool choice justification.
*   Node.js / Yarn Justification (p. 31-32): Tool choice justification.
*   TypeScript Justification (p. 33): Language choice justification.
*   React 19 / Next.js 15 Justification (p. 34-36): Framework version justification.
*   Turbopack / Next/Babel Config (p. 40-43): Tool configuration.
*   SonarQube / New Relic (p. 49-50): Tool choices.
*   Autenticación Strategy (JWT/Middleware) (p. 50-52): Architectural pattern description.
*   Estructura de los proyectos (p. 67-69): High-level directory structure, less suitable for fine-grained rules unless specific patterns are enforced within files. 