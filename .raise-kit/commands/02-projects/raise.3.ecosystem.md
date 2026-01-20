---
description: Map the ecosystem of an existing system, including services, integrations, and data flows.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Map the surrounding ecosystem of services, APIs, and infrastructure following the `patron-02-ecosystem-discovery` pattern.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load template from `.specify/templates/raise/sar/informe_mapa_dependencias.md`.

2. **Ecosystem Discovery Flow**:
   - **Identify Connected Systems**: Search for endpoints, config files, and API clients in the code.
   - **Map Communication Protocols**: Identify protocols (REST, gRPC), auth methods, and data formats.
   - **Document Data Flows**: Trace where data comes from and where it goes.
   - **Verificación**: Existe al menos una integración identificada o confirmación de sistema autocontenido.
   - > **Si no puedes continuar**: Sin integraciones externas → Generar un diagrama minimal indicando "Sistema autocontenido" con advertencia de que no se detectaron dependencias externas.

3. **Classification & Risk Analysis**:
   - Classify as Upstream, Downstream, or Peer.
   - Prioritize by criticality: Critical, Important, Optional.
   - Identify risks (missing fallbacks, SLAs, circular dependencies).
   - **Verificación**: Cada integración tiene asignada una criticidad y riesgos identificados.
   - > **Si no puedes continuar**: Integraciones no documentadas en el repo → Marcar en el informe como "Descubierta por análisis de código" y solicitar validación al usuario.

4. **Generate Artifact (Ecosystem Map)**:
   - Create/Update `specs/main/analysis/informe_mapa_dependencias.md` in **Spanish**.
   - MUST include a **Mermaid** diagram (`graph TD`) showing all services.
   - Provide the integration table with: name, protocol, type, criticality, and risks.

5. **Quality Validation**:
   - Verify every system in the diagram has a corresponding entry in the table.
   - Ensure the diagram is readable and organized by domain.

6. **Finalize**:
   - Run `.specify/scripts/bash/update-agent-context.sh gemini`.
   - Confirm file existence with `check_file "specs/main/analysis/informe_mapa_dependencias.md" "Ecosystem Map"`.

## High-Signaling Guidelines

- **Focus**: Strategic visibility of connectivity and dependencies.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Do not hallucinate external systems; report only what is in code/config.

## AI Guidance

When executing this workflow:
1. **Be Evidence-Based**: Identify "shadow" integrations from clients found in code.
2. **Visual Clarity**: Spend effort organizing the Mermaid diagram to be understandable in seconds.
3. **Risk Exposure**: Focus on the business impact of a dependency failure.
4. **Gates**: Cross-reference with the architecture report if generated.

## High-Signaling Guidelines

- **Focus**: Connectivity and risk management.
- **Language**: Instructions English; Content **SPANISH**.
- **Visual Mapping**: Prioritize Mermaid diagrams for clarity.

## AI Guidance

When executing this workflow:
1. **Verification**: Don't just rely on documentation; verify URLs and clients in the code.
2. **Shadow IT**: Identify "shadow" integrations that aren't in official architecture docs.
3. **Pace**: Ensure the map is understandable by a newcomer in < 15 minutes.

