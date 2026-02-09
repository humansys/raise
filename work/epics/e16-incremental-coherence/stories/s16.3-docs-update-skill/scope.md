# S16.3: Docs Update Skill

## Scope

**In:**
- `/docs-update` skill definition (Claude skill YAML + prompt)
- Compares knowledge graph vs module architecture docs
- Updates frontmatter (status, dependencies, components) deterministically
- Updates narrative sections via inference (description, responsibilities, interfaces)
- HITL gate before writing changes
- Invocable standalone and as subagent from lifecycle skills

**Out:**
- Lifecycle wiring into story-close (S16.4)
- Discovery pipeline re-run (separate task)
- Changes to the graph diff engine (S16.2, done)

## Done Criteria
- [ ] `/docs-update` skill exists and is loadable
- [ ] Skill compares graph data against current module docs
- [ ] Frontmatter updates are deterministic (CLI-generated, not inference)
- [ ] Narrative updates use inference with HITL review
- [ ] Works standalone (`/docs-update`) and as subagent
- [ ] Tests pass for any new CLI code
- [ ] Retrospective complete
