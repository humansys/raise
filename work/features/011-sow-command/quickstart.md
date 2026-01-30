# Quickstart: Generate Statement of Work

Command: `/raise.7.sow`

## Prerequisites

Ensure the following upstream artifacts exist in `specs/main/`:
1. `project_requirements.md` (PRD)
2. `solution_vision.md` (Vision)
3. `tech_design.md` (Tech Design)
4. `project_backlog.md` (Backlog)
5. `estimation_roadmap.md` (Roadmap)

## Usage

1. **Run the command**:
   ```bash
   /raise.7.sow
   ```

2. **Review inputs**:
   The agent will verify all files exist. If any are missing, it will stop and ask you to create them using previous commands (e.g., `/raise.6.estimation`).

3. **Validate Output**:
   The `statement_of_work.md` file will be generated in `specs/main/`.
   - Review the **Pricing** section (Section 9) to ensure costs match the Roadmap.
   - Review **Timeline** (Section 5) for accuracy.
   - Verify **Exclusions** (Section 8) are correctly carried over from the PRD.

## Troubleshooting

- **"File not found"**: Check that you are in the correct root directory and that `specs/main` is populated.
- **"Template missing"**: Ensure `.specify/templates/raise/solution/statement_of_work.md` exists. Run `/speckit.constitution` to refresh templates if needed.
