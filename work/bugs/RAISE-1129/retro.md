## Retrospective: RAISE-1129

### Summary
- Root cause: Al separar repos raise-commons/raise-gtm, no se creó pipeline de deploy para docs/
- Fix approach: Bootstrap MkDocs + Material, eliminar Astro site/, crear deploy-docs.yml

### Heutagogical Checkpoint
1. Learned: Los .mdx del proyecto no usaban componentes JSX — eran markdown puro con frontmatter. La migración a MkDocs fue trivial (rename + fix links). La complejidad de Astro no aportaba nada.
2. Process change: Al separar repositorios, crear checklist explícito de "qué pipelines necesitan crearse para cada repo". La separación de raise-gtm dejó un hueco porque nadie verificó que docs tuviera su propio deploy.
3. Framework improvement: El skill de bugfix funcionó bien para estructurar el trabajo. El análisis 5-Whys fue útil aunque la causa era evidente — forzó documentar la cadena causal completa.
4. Capability gained: MkDocs bootstrap pattern — ahora sabemos que la migración Astro→MkDocs para contenido sin componentes es un rename + fix links + mkdocs.yml.

### Patterns
- Added: pending (repo-split-checklist)
- Reinforced: none evaluated
