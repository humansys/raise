Perfect. I’ll research the best practices for designing an autonomous agent (Claude Sonnet 3.5+) that manages and evolves a `.cursor/rules` system across a team repo. This will include:

1. A clear process for initializing and maintaining Cursor rules collaboratively.
2. Recommendations for MCP server tools the agent should expose in Cursor IDE.
3. An agentic system prompt designed to allow the agent to safely propose and revise rule files using Git-based version control, with human-in-the-loop approval for major updates.

I’ll bring everything together in a structured process guide and a ready-to-use agent system prompt. I’ll follow up soon with the results.

# Managing Cursor Project Rules with an Autonomous Claude Agent

Project-specific Cursor rules (introduced in Cursor v0.47+) are stored under the `.cursor/rules` directory and act as custom instructions to guide the AI model’s behavior ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Using%20rules%20in%20Cursor%20you,a%20system%20prompt%20for%20LLMs)). They provide **granular control** over AI assistance in different parts of a project (via path-specific configurations and glob matching) ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Project%20rules%20offer%20a%20powerful,different%20parts%20of%20your%20project)). Using an autonomous Claude Sonnet 3.5 agent as a team assistant, a development team can create and maintain these rules so that AI code generation remains consistent with the team's standards. The agent will operate with a high degree of autonomy in drafting and proposing rule changes, but always with human-in-the-loop approval for applying those changes. 

Below, we outline:

1. **Process documentation** for setting up initial Cursor rules and evolving them over time with the agent.  
2. **Design of an MCP-based agent interface** in Cursor to support this workflow.  
3. A **detailed system prompt** for the Claude agent to fulfill this role, following best practices from Cursor’s documentation and Anthropic’s guidelines.

## 1. Process Documentation Guide: Creating and Updating Cursor Rules

### Initial Setup of `.cursor/rules` for a Project

- **Codebase Analysis**: The agent begins by analyzing the project to determine relevant rules. It inspects the tech stack, frameworks, and any existing style guides or linters. For example, it may detect a React/TypeScript frontend, a Python backend, specific testing frameworks, or coding conventions from configuration files. This baseline understanding informs what rules will be needed.

- **Drafting the Rule Files**: Using the analysis, the agent creates initial rule files in `.cursor/rules`. Each rule is stored as an `.mdc` file (Multi-Document Context), which is essentially a YAML-based markdown file (the agent must use valid YAML, as only `.mdc` YAML files are recognized as rules) ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=AI%20to%20see%20what%20it,thought%20the%20docs%20were%20saying)). The agent should:  
    - Choose a clear naming convention and ordering for the files. A common practice is to prefix filenames with numbers to enforce load order (e.g. `001-core-guidelines.mdc`, `100-api-conventions.mdc`, etc.) ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=Through%20trial%20and%20error%2C%20I,and%20group%20rules%20like%20this)). Lower-numbered “core” rules load first, and higher-numbered specialized rules can override settings if necessary (when rules conflict, the last one wins in Cursor’s system) ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=on%20the%20numbers%20,gets%20to%20pick%20the%20temperature)).  
    - Within each `.mdc`, include a YAML front matter with fields like `name` (rule name), `version` (rule version), `globs` (file patterns to which the rule applies), and `triggers` (when to activate; e.g. on file open or save) ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=,%60%60%60yaml)). For instance, a rule targeting all Python files might have `globs: ["**/*.py"]` to apply it project-wide, or a narrower pattern for a specific directory.  
    - Provide a description of the rule’s purpose (either in the YAML or as comments). This description acts as semantic guidance for when the rule should be applied ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=,when%20the%20rule%20is%20applied)). For example, “This rule enforces PEP8 style on all Python code” gives context to both the team and the AI about why the rule exists.  
    - Ensure the content of the rule instructs the AI appropriately. Rules can include guidelines like coding style preferences, architectural patterns to follow, or prohibitions (e.g. “Do not use `eval`”). Essentially, these are directives that will be injected into the AI’s context when relevant files are being edited ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Using%20rules%20in%20Cursor%20you,a%20system%20prompt%20for%20LLMs)).

- **Human Review of Initial Rules**: Once the agent drafts the initial set of rules, it should present them to the team for approval. This could be done by opening the new `.mdc` files in the IDE for the developer to review, or by summarizing the rules in a report. The team checks that the rules correctly capture their intentions (e.g. confirm that framework-specific rules match their actual practices, that coding style rules align with their style guide, etc.). This review is crucial to ensure the AI won’t be guided by a misunderstanding of the project.

- **Version Control Commit**: After approval, the initial rules are added to the repository. Because the rules reside in the project directory, they can be managed with Git like any other code file ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=You%20can%20create%20a%20new,since%20it%E2%80%99s%20just%20a%20file)). The agent (or developer) creates a commit (for example, “chore(rules): add initial Cursor project rules”) adding the `.cursor/rules` directory. This establishes a baseline rule set that will evolve alongside the codebase.

### Ongoing Evaluation and Proposal of Rule Updates

- **Continuous Monitoring**: As development progresses, the agent continuously monitors the codebase and development process for triggers that suggest a rule change. For example:  
  - New patterns in code – e.g. the team adopts a new library or architectural pattern. The agent notices new file types or repeated code structures (say, many React functional components using a certain hook) and considers if a rule should document the best practice for them.  
  - Repeated feedback in code reviews – e.g. if multiple PRs have reviewer comments like “We should always handle null inputs here,” the agent identifies this as a candidate for a new rule about input validation.  
  - AI output corrections – if developers frequently have to correct the AI’s suggestions in a similar way, it indicates a gap. For instance, if the AI often suggests using an outdated function and the developer replaces it every time, a rule might be needed to steer the AI toward the correct function.

- **Proposing Changes**: The agent formulates rule updates in response to these observations:  
    - It may draft a new `.mdc` file if a new area needs coverage (for instance, introducing `210-database-queries.mdc` if database query patterns emerge that aren’t covered by existing rules).  
    - Or it may edit an existing rule file to refine it (for example, expanding a rule’s glob pattern to include a new directory, or updating a rule’s guidance as the project’s code style evolves).  
    - The agent ensures any new or edited rule still uses proper YAML syntax and fits into the established naming/order scheme. It might bump a `version` field in the rule’s metadata to indicate an update, if versioning is used.  
    - Each proposed change is kept as **atomic** as possible – focusing on one specific issue. This makes reviews easier and traceability clearer, with one commit or proposal per distinct rule change.

- **Draft Review Process**: For every proposed update, the agent prepares a clear explanation and *diff*:  
  - It may open a preview of the changes in Cursor’s UI or, if interacting via chat, provide a unified diff snippet showing exactly what lines will change in which `.mdc` file.  
  - Alongside the diff, the agent explains *why* this change is suggested. For example: “Added a new rule to enforce checking for `None` inputs in service functions, because in the last two PRs reviewers noted missing null-checks. This will remind the AI to include those checks.”  
  - The agent uses references from the code or team discussions to justify the change. This context is critical for the team to understand the necessity of the rule. It’s similar to writing a good commit message or PR description for a code change, but here it’s about an AI guidance change.

- **Human-In-The-Loop Approval**: The team reviews the agent’s suggestions. No rule change goes live without a human developer’s sign-off. This can happen in a few ways:  
  - Within Cursor IDE, the agent might prompt the user in chat: “I have a suggestion to update the AI rules. Would you like to review it?” The developer can then inspect the diff and approve or reject it.  
  - If using a Git-based workflow for changes, the agent could open a pull request or commit for the proposed rule change (in a separate branch), which team members then review using normal code review tools. The agent’s diff and explanation would be included (for example, the agent could post the diff and rationale as the PR description or a comment). In a community example, a GitHub bot approach was taken where the bot replied to PR comments with suggested rule diffs and waited for an “accept” command ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=The%20key%20idea%20is%20that,on%20feedback%20from%20those%20PRs)) ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=2,the%20rules%20to%20the%20branch)). In Cursor’s case, the agent can play a similar role interactively.  
  - This step aligns with Anthropic’s recommended pattern that agents should pause for human judgment at decision points ([Building Effective AI Agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents#:~:text=either%20a%20command%20from%2C%20or,such%20as)) – the agent operates independently to identify and draft changes, but defers to a human for final approval.

- **Incorporation and Iteration**: Once approved, the agent (or a developer, if they prefer to apply manually) incorporates the change:  
  - The `.mdc` files are updated in the repository and committed, e.g. “feat(rules): add input validation rule for service layer”. Over time, a history of such commits accumulates. Team members can consult the Git log to see why a rule was added or changed, since each commit message and diff provides context. (This is useful for onboarding new members or auditing the AI configuration.)  
  - The agent records these changes to avoid flip-flopping. For example, if a rule was deliberately removed or loosened, the agent should not reintroduce it later unless circumstances truly change and a human agrees.  
  - If a rule update does not achieve the intended effect (maybe the AI still makes a certain mistake), the process repeats: the agent can refine the rule or add another to supplement it. The system is meant to evolve iteratively.

- **Best Practices in Maintenance**:  
  - **Maintain consistency**: The agent should ensure that new rules do not conflict with existing ones unless intentionally meant to override (and if so, the override should be documented). If two rules inadvertently conflict (e.g., one rule says "use semicolons" and another says "omit semicolons"), the agent should catch that and resolve it with the team (perhaps by merging them or adjusting scope).  
  - **Stay current with the code**: Remove or update rules that become outdated. For instance, if a rule references a function or library that the project has deprecated, that rule should be revised or eliminated to avoid confusing the AI.  
  - **Solicit feedback**: The agent can periodically ask the team if the AI’s suggestions are meeting expectations. If developers are consistently happy or if they are repeatedly overriding the AI in certain cases, that’s valuable feedback. For example, if developers keep ignoring an AI suggestion that follows a rule, maybe that rule is too strict or not applicable, and should be adjusted.  
  - **Treat rules as living documentation**: Remind the team that `.cursor/rules` is effectively the AI’s "guidebook" for the project. Keeping it clean and relevant is as important as maintaining good developer documentation or a style guide, since it directly affects AI outputs.

### Team-Wide Rule Maintenance Best Practices

- **Version Control and Collaboration**: Treat the `.cursor/rules` directory as a first-class part of the project. All changes to rules should be tracked in Git, just like code changes. Use pull requests or merge requests for rule updates so they undergo peer review ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=3,the%20rules%20to%20the%20branch)). This not only catches possible issues (like a rule that might have unintended consequences) but also creates an audit trail of how the AI’s instructions have evolved over time.  
  - Because Cursor project rules are just files in the repo, you get the benefits of branching and merging for free ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=You%20can%20create%20a%20new,since%20it%E2%80%99s%20just%20a%20file)). For example, if the team is experimenting with a new framework, they might develop new rules in a feature branch alongside the code, and merge them when ready.  
  - Use descriptive commit messages for rule changes. It helps to prefix them in a way that’s easy to spot (some teams use `rules:` or `ai:` as a tag). If your team follows Conventional Commits, you might classify rule updates as `chore: ai rules` or `docs: ai rules` unless they directly affect code functionality. (Cursor’s AI commit generation can pick up your conventions and follow suit ([AI Commit Message - Cursor](https://docs.cursor.com/more/ai-commit-message#:~:text=AI%20Commit%20Message%20,will%20follow%20the%20same%20pattern)).) The key is to make the intent clear – e.g., “rules: add guidance on API error handling [based on recent review feedback]”.

- **Rule File Organization**: Establish a clear structure for rule files so the entire team understands where to find or add rules:  
  - Group rules by domain or layer. For instance, you might reserve `0xx` for general coding standards, `1xx` for frontend-specific rules, `2xx` for backend/API rules, `3xx` for testing/CI rules, etc., as one community member suggested ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=Through%20trial%20and%20error%2C%20I,and%20group%20rules%20like%20this)). This way, related rules live nearby in the sorted order and it’s obvious where a new rule should go.  
  - Keep individual rule files focused. Instead of one monolithic rule file, have multiple files each covering a cohesive topic (e.g., a file for logging practices, another for security checks, another for code style). This modularity means the AI will include only the relevant rules based on context (Cursor will load only those whose glob patterns match the files in question).  
  - Use comments and markdown within rule files to clarify things. The `.mdc` format supports including markdown content, so you can have sections or bullet points inside a rule file explaining the rationale. For example, a rule file could contain a list of do’s and don’ts for writing SQL queries in the project. This not only guides the AI but also serves as human-readable documentation.

- **Periodic Audits**: Schedule regular check-ins (perhaps each sprint or at project milestones) where the team and the agent review the rules together:  
  - **Cleanup**: Remove rules that no longer make sense and simplify any that are too complicated. Over time, some rules might become irrelevant or redundant; cleaning them prevents clutter and confusion.  
  - **Impact assessment**: Discuss whether the rules are having the desired effect. Are developers seeing better AI suggestions? Are there fewer style fixes needed in PRs? The agent can provide some data here, like “I haven’t seen any suggestions violating rule X in a while” or “Developers have overridden the AI on Y several times this month, maybe we need a new rule or to adjust one.”  
  - **Team alignment**: Ensure the rules still reflect the team’s consensus. Teams change and standards evolve; the rules should evolve too. These audit meetings can surface changes in opinion, like deciding to adopt a new coding style or pattern, which the agent can then help encode into updated rules.

- **Onboarding New Projects/Members**: If a new project is started or a new developer joins the team:  
  - For new projects, consider borrowing from existing rules. The agent (with permission) might use rules from a similar project as a starting point, then customize them. Cursor also allows Global Rules (user-level rules that apply to all projects) ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Rules%20applied%20globally%20to%20all,section)) for things like personal preferences, but project rules should capture the specifics of each project’s needs.  
  - Make sure new team members are aware of the rules. The agent or a team lead can walk them through the `.cursor/rules` directory. Because these rules essentially encode the team’s best practices, reviewing them is a great way to get up to speed on how the team likes to code. The agent could even have a command to summarize the rules for a newcomer (for example, listing the key points of each rule file).

- **Encourage Team Input**: The rules system works best when it captures collective knowledge. Encourage team members to suggest improvements to the rules whenever they encounter the AI doing something suboptimal or when they have a new insight:  
  - For example, during a PR review, if someone comments “We should avoid using X function because it’s deprecated,” that could become a rule. The agent can be invoked to draft such a rule on the spot or after the fact. In one workflow, a bot monitored PR comments and automatically suggested rule changes based on them ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=The%20key%20idea%20is%20that,on%20feedback%20from%20those%20PRs)). In Cursor, a developer could simply tell the agent in chat, “Add a rule about avoiding X function,” and let it draft one for review.  
  - The agent could also monitor commit messages or issue tracker for clues (e.g., a bug report that says “lack of input validation caused an error” might hint at adding a rule for input validation). While this is advanced, it illustrates that any source of team knowledge can feed into rule evolution.  
  - By treating the agent as a partner, team members will over time offload more of the standards enforcement to it. This not only saves effort (fewer repetitive comments in code reviews) but also ensures the AI is truly tailored to the team.

By following these processes, the team establishes a robust workflow where the AI assistant’s behavior is continually aligned with team standards. The `.cursor/rules` directory becomes a reliable, version-controlled source of truth for how the AI should behave, and the agent ensures it stays up-to-date as the project grows.

## 2. MCP Agent Interface Design in Cursor

To integrate this autonomous agent into Cursor IDE, we leverage Cursor’s **Model Context Protocol (MCP)** plugin system ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=What%20is%20MCP%3F)). MCP allows external tools and services to provide context and functionality to the Cursor AI agent via a standardized interface ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=The%20Model%20Context%20Protocol%20,and%20tools%20through%20standardized%20interfaces)) ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=MCP%20servers%20can%20be%20written,and%20technology%20stack%20very%20quickly)). In this case, our agent will run as an MCP server, exposing specific tools/commands that enable it to manage the `.cursor/rules` files and interact with the development workflow. We need to design what tools it offers, how the agent uses them, and how developers interact with the agent through Cursor.

### Tools and Commands Exposed by the Agent’s MCP Server

The agent’s MCP server should expose a set of tools that allow it to read, modify, and suggest changes to rule files (and possibly interface with version control). According to Anthropic’s best practices for tool-using agents, each tool should have a clear purpose and be easy for the model to use without confusion ([Building Effective AI Agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents#:~:text=,many%20example%20inputs%20in%20our)). Here are key tools and commands to include:

- **Project Inspection Tools**:  
  - `list_files(pattern)`: Returns a list of file paths in the repository matching the given glob pattern. The agent will use this to discover files relevant to rule generation (for example, `list_files("**/*.py")` to find all Python files, or `list_files("**/package.json")` to see if a Node.js package file exists).  
  - `read_file(path)`: Returns the contents of the file at the given path. This lets the agent examine code or config files. For instance, reading a `pyproject.toml` might tell it the coding style or dependencies, or reading an existing `.cursor/rules/` file lets the agent check current rules.

- **Rule Management Tools**:  
  - `write_file(path, content)`: Creates or updates a file with the given content. The agent will use this to write new `.mdc` files or update existing ones. Importantly, we **do not enable “Yolo” mode** for this tool – meaning every call to `write_file` will require user confirmation in Cursor by default ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=match%20at%20L253%20You%20can,how%20to%20enable%20it%20here)). This ensures the agent never writes out changes without a developer explicitly allowing it (the human-in-loop safeguard).  
  - `generate_diff(path, new_content)`: Reads the current file at `path` (if it exists) and generates a unified diff between the current content and `new_content`. The agent can use this to show the developer exactly what changes it intends to make to a rule file *before* actually writing those changes. This is extremely helpful for transparency – the agent doesn’t have to rely on the model to format a diff (which can be error-prone ([Building Effective AI Agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents#:~:text=There%20are%20often%20several%20ways,escaping%20of%20newlines%20and%20quotes))); instead, a diff tool guarantees accuracy in the patch. The output can be presented in the chat for review.  
  - *(Optional)* `append_file(path, content)`: In case we want to allow appending to logs or changelogs, a separate tool could handle that. But the agent can also use `read_file` + `write_file` to achieve an append if needed. This is less crucial than the above.

- **Version Control / Collaboration Tools**:  
  - `commit_changes(message)`: Stages any pending file changes (from prior `write_file` calls) and creates a Git commit with the given commit message. This automates the final step of rule update application. Cursor’s agent could call this once a diff is approved by the user. The commit message can be suggested by the agent (and the agent should follow any team conventions in the message, as it will have observed past commits).  
  - `open_pr(title, description)`: If the project is connected to a git remote and the team wants the agent to open pull requests for rule changes, this tool would create a PR with the provided title and body. This is more complex and requires configuration (GitHub/GitLab credentials, etc.), so it might be an optional extension. Many teams might be fine with local commits and then manually pushing to a remote if needed.  
  - `run_tests()` or other project-specific tools: Depending on how integrated we want the agent, we could also give it tools to run the project’s tests or linters. For example, after adding a rule, it might run `npm run lint` or similar to ensure it didn’t break anything or to gather more context. However, these extend beyond rule management into CI territory, and would be configured on a project-by-project basis.

- **Informational/Interaction Tools**:  
  - The agent primarily communicates via text in the chat, so explicit tools for explanation aren’t strictly needed (the agent can just write to the chat). However, it might be useful to have a `describe_rules()` command that compiles a summary of all current rules. The agent could call this internally or it could just directly read all `.mdc` files and summarize.  
  - Another could be `get_rule_history(rule_name)` if we stored a changelog or had access to Git history via an API. This would let the agent explain when and why a rule was last changed by pulling commit info. This is a nice-to-have for transparency.

These tools would be registered in the project’s MCP config (e.g., `.cursor/mcp.json`) so that Cursor knows how to connect to the agent’s server and advertise these capabilities ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=match%20at%20L222%20For%20tools,available%20within%20that%20specific%20project)). Each tool should have a clear natural-language description in the MCP config, as per Anthropi’s guidance, so Claude (the model) knows when and how to use them. For example, `generate_diff`’s description might say: “Use this tool to see the differences between a file’s current content and proposed new content. Input: file path and new content. Output: a diff in unified format.” This clarity helps the agent choose the right tool at the right time ([Building Effective AI Agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents#:~:text=,many%20example%20inputs%20in%20our)).

### Agent Usage During Project Onboarding

When a project is first set up in Cursor (or when introducing the agent to an existing project without rules), the interface should support a smooth onboarding sequence:

1. **Initialization Trigger**: A developer can manually initiate rule setup. For instance, they might use Cursor’s command palette (`Cmd+Shift+P`) and select a command like “Initialize Cursor Project Rules” (wired to the agent), or simply ask in the AI chat: “Set up project rules for me.” The agent could also automatically suggest this if it detects that `.cursor/rules/` is empty or the project is new.

2. **Data Gathering**: The agent uses the Project Inspection tools to scan the repository. It might call `list_files` on various patterns to see what languages are present (e.g., any `.java` files? any `.py` files? etc.), and `read_file` on key files like package manifests or existing documentation. This step gives it an outline of the project’s nature. For example, reading a `README.md` might reveal the project is a “Django web app” or “React Native mobile app,” which immediately informs the kind of rules needed.

3. **Rule Drafting**: Based on what it found, the agent drafts a set of initial rules (as described in the process guide earlier). Suppose it identified a Python backend and a TypeScript frontend: it will create Python-specific rules (maybe referencing PEP8, type hints, etc.) and TypeScript/React rules (code style, project structure conventions, etc.). The agent might internally prepare the content of several `.mdc` files at this point.

4. **Presenting for Review**: Before writing any files, the agent should present its plan to the user. Using `generate_diff`, it can show what *would* be written. Since these are new files, the “diff” is essentially the full content of each file (added lines). The agent can display something like: 

   **Proposed Rule: 001-core-guidelines.mdc** (with a diff showing the entire file as additions)  
   **Proposed Rule: 100-python.mdc** (diff with content)  
   **Proposed Rule: 200-frontend.mdc** (diff with content)

   And so on. Each diff can be accompanied by the agent’s explanation: “001-core-guidelines.mdc contains general rules (coding style, license header, etc.) that apply to all files. 100-python.mdc has Python-specific best practices (we detected a Django project, so it includes Django conventions). 200-frontend.mdc covers React/TypeScript patterns.” This breakdown makes it easy for the developer to review piece by piece.

5. **Incorporating Feedback**: The developer might say, “Looks good, except our style guide says 120-character line length, not 80.” The agent can then modify the relevant rule in its draft (perhaps a line in core guidelines about line length) and show an updated diff. This interactive tweaking continues until the developer is satisfied.

6. **Apply Changes**: Once approved, the developer instructs the agent to apply the rules (or clicks “Approve” on each diff in the Cursor UI). The agent then uses `write_file` to create each of those `.mdc` files in the `.cursor/rules` directory. Immediately, those rules become active for the AI. The agent then likely calls `commit_changes` with a message like “chore(rules): add initial project rules [AI assistant initialized]”. If the project is connected to a remote repository, the developer can push this commit, or the agent could even use `open_pr` to create a PR on GitHub for visibility.

Throughout onboarding, **human approval is required at critical points**. The interface, by design, will not let `write_file` or `commit_changes` execute without user consent (unless the team explicitly turns on autonomous mode). This ensures the initial setup is done *with* the team, not just for the team, building trust in the agent.

### Daily Development Workflow Integration

Once the project has a rules system in place, the agent becomes a continuous assistant during development. The MCP interface supports this in several ways:

- **Automatic Contextual Assistance**: Thanks to Cursor’s mechanism, whenever a developer is editing code, the relevant project rules are automatically pulled into the AI’s context (based on file path matching) ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=,when%20the%20rule%20is%20applied)). This means the agent’s work (the rules) is being applied behind the scenes on every AI generation. The agent doesn’t need a special tool here; it’s how Cursor’s core works. But the result is that the developer experiences an AI that is tailored to their project.

- **Ad-hoc Rule Queries**: A developer can query the agent about the rules via chat. For example, “@Agent, what rules are active for this file?” The agent can then use `list_files`/`read_file` to find which rules `.mdc` apply to the file’s path and summarize them. Or a question like “Do we have any rule about database transactions?” might prompt the agent to search the rules (perhaps just grep through `.cursor/rules` content via its knowledge or a simple tool) and respond accordingly. This turns the agent into a handy reference for team policy, similar to asking a teammate “Do we have a guideline for X?”.

- **On-Demand Rule Updates**: If a developer suspects the AI could do better in a certain scenario, they can prompt the agent to update the rules. For instance, “The AI isn’t adding error handling in new API functions. Can you fix that?” The agent would then investigate (maybe it finds that indeed many new API functions lack try/except) and propose a new rule or update. This uses the same propose-review-apply cycle described earlier, just initiated by a human command. The MCP interface doesn’t need a special command for this beyond the normal chat; it’s more about the agent understanding the request.

- **Proactive Suggestions (Agent-Initiated)**: The agent can also take initiative when certain triggers occur:  
  - **After Large Code Changes**: Suppose a developer just merged a significant refactor or added a big feature (lots of new files). The agent, noticing this (perhaps via a hook or simply by seeing many new files on disk), could perform a scan and say in chat, “I noticed 5 new modules added for feature X. Would you like me to review our rules to see if any updates are needed?” This prompt can lead the developer to either say “Sure” (and the agent then analyzes and maybe finds something to add) or “Not now.”  
  - **During Pull Request Review**: If the team uses Cursor during PRs (Cursor might not manage PRs directly, but the agent could be used on diffs), the agent could parse the diff and comments. In the GitHub bot example, whenever a PR comment was posted, the bot checked if it was a rule-related suggestion ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=The%20key%20idea%20is%20that,on%20feedback%20from%20those%20PRs)). In Cursor, an analogous situation is a developer making a comment in code or even in commit message (e.g., “TODO: we should enforce this pattern”). The agent interface could include a way to ingest such comments. Perhaps a tool that reads recent commit messages or a convention that special comments trigger the agent. Designing this would involve specifying what events from source control Cursor can forward to the agent. Alternatively, the agent simply periodically runs `list_files` to see if any new `TODO` or `NOTE` comments in code match known patterns.  
  - **Scheduled Review**: The team might set the agent to do a weekly scan. This could be as simple as the team lead asking every Friday, “@Agent, do we need any rule updates based on this week’s work?” The agent then goes through its monitoring routine and reports.

- **Developer Workflow Integration**: The agent’s suggestions and actions appear in the normal development flow, not as separate systems. For example, if it proposes a rule change, the developer sees a diff and message in their Cursor chat or maybe as a notification. Approving it might be clicking a button or typing “Yes, apply.” This tight loop means the team doesn’t have to leave their IDE or go to an external dashboard to manage AI behavior. It’s all in one place, making it more likely to be maintained actively.

- **Reviewing Diffs and Rationale**: The interface is designed to make review easy. When the agent uses `generate_diff` and outputs a diff in the chat, Cursor will format that diff in a readable way (monospaced font with colored additions/deletions in many cases). For example, the agent might show a diff like: 

  ```diff
  +# New rule: ensure all API functions validate inputs
   rule_definition:
     description: "Enforce input validation in API functions."
  ```
  
  to indicate it’s adding a new section to a rule file (the actual diff would be more extensive, including file creation or content). The developer can scroll through this within chat or click to open the affected file directly. The explanation accompanying the diff will say why this change is proposed, often referencing specific instances that triggered it.

- **Approval via Interface**: Cursor’s UI for MCP tool usage will prompt for confirmation for any `write_file` or `commit_changes` call. So when the agent is ready to apply something, the developer might see a dialog or a highlighted prompt saying something like: “Tool `write_file` is about to run, creating `210-api-validation.mdc`. Allow?” The developer can accept, possibly after reviewing the diff shown. Similarly, for `commit_changes`. This UI feedback ensures nothing happens silently. If something is unclear, the developer can refuse and ask the agent further questions.

- **Logging and State**: The MCP interface can keep some state if needed. For example, the agent’s server might log all suggestions and whether they were accepted or not. If a suggestion is declined, it could record that to avoid spamming the same suggestion again. In practice, the agent’s memory (context window) might suffice for this, but for long-running autonomy, a small external state (even in a JSON file) could be maintained to remember what it has proposed previously. Exposing a tool like `get_agent_state` could allow debugging this, but it might not be necessary for normal operation.

- **Error Handling**: If a tool fails (say `read_file` on a path that doesn’t exist, or `commit_changes` when there are no changes to commit), the agent should handle it gracefully, inform the user if needed, or correct its assumptions. The MCP interface will typically return error messages which the agent can see. For example, if `commit_changes` returns “Nothing to commit”, the agent might realize someone already committed or there were no changes, and then inform the user or adjust its plan.

In summary, the MCP interface design ensures the agent has *capabilities* to do its job (inspect code, propose changes, apply changes) but uses Cursor’s built-in approval and context mechanisms to keep the human in charge. The developers can interact with the agent conversationally, and all proposals are visible and reviewable just like code changes, making the agent a natural extension of the team’s workflow.

### Human-in-the-Loop and Transparency Features

The design emphasizes high autonomy with human oversight, so we include specific interface features to support that:

- **No Autonomous Writes without Consent**: By not enabling Yolo mode for destructive actions, we rely on Cursor’s tool approval prompts ([Cursor – Model Context Protocol](https://docs.cursor.com/context/model-context-protocol#:~:text=The%20Composer%20Agent%20will%20automatically,determines%20them%20to%20be%20relevant)). This means even if the agent decides to make a change at 3am, if no one is there to approve, it simply won’t execute. It might queue the suggestion, but a developer will see it the next morning and approve or deny it. This ensures control and also provides a chance to discuss changes if needed.

- **Diff-Based Review**: The use of `generate_diff` for showing changes means the agent is never saying “Trust me, I updated the file.” It’s always “Here’s exactly what I will do, line by line.” This transparency builds trust. Even non-experts on the team can read a diff and understand a rule change, whereas reading a full raw `.mdc` file might be more effort. The interface displaying diffs, with lines added/removed, leverages developers’ existing skills (code review) for reviewing AI rules changes.

- **Clear Justification**: The interface (chat) encourages the agent to provide reasoning with each suggestion. The system prompt (below) will instruct the agent to always explain “why” it’s doing something. As a result, when using the interface, developers will see messages like “(Agent): I suggest this change because our codebase switched from library X to library Y last week, and the old rule about X is now irrelevant.” If the explanation isn’t clear, the developer can ask follow-up questions in chat. The interface thus facilitates a dialog, not just one-shot suggestions.

- **Audit Trail**: After changes are made, because they are committed to Git, the history is preserved outside the agent. Even if the agent’s memory is reset or a new agent comes in, the repository’s commit log shows what happened. To make this easier to parse, commit messages should contain keywords or tags. For example, the agent might always include `[CursorRules]` in the commit message or something like that, so one can filter the Git log. In design, we might instruct the agent on commit message format to ensure this.

- **Fallback to Human Guidance**: If the agent is unsure or encounters ambiguity, the interface allows it to ask the user. For example, maybe the agent sees a new coding pattern but isn't sure if it's intentional or an oversight. It might ask, “I noticed several functions using global variables. Do we want a rule to discourage that?” The developer can then respond with their preference. This kind of query is done via the chat interface, treating the human as another “tool” (in the sense that the agent can always converse to get clarification). It’s important the agent doesn’t hesitate to involve the human when needed; the interface should make that as frictionless as the agent calling any other tool.

- **MCP Server Management**: We should also consider how the agent’s MCP server is run and managed. Likely it starts when Cursor launches or the project opens. The design could include a status indicator (e.g., “Rules Agent: Connected” in the IDE) and controls (like restart agent, view agent logs). While not purely in the conversational interface, these ensure that if the agent gets stuck or has an issue, the developers have recourse (restart it or check logs for errors). This reliability aspect is important for team adoption.

By incorporating these human-in-loop and transparency features, we ensure the agent remains a **team assistant** and not an automated overlord. Developers see *what* it’s doing, *why* it’s doing it, and have ultimate say on whether it happens. Over time, as trust builds, the team might grant the agent a bit more leeway on trivial changes, but the system is set up such that even then, everything is logged and visible.

## 3. System Prompt for the Claude Sonnet 3.5 Agent

Below is a detailed **system prompt** for the Claude Sonnet 3.5 agent responsible for managing the Cursor rules system. This prompt is designed to be production-ready, instructing the agent on its role, the tools it has, and how to handle various scenarios. (Explanatory comments are included in brackets for clarity but would not be part of the actual prompt.)

```
You are "CursorRules-GPT", an autonomous team assistant integrated into Cursor IDE. Your primary job is to help maintain the project’s AI assistant rules (the files in `.cursor/rules/`) to ensure consistent, high-quality code generation aligned with the team’s practices.

## Role & Objectives:
- **AI Code Guardian**: Continuously monitor the project’s code and development feedback to identify best practices, style guidelines, and patterns that should be enforced or encouraged in AI-generated code. These are codified as Cursor project rules (which function like a custom system prompt for the AI) ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Using%20rules%20in%20Cursor%20you,a%20system%20prompt%20for%20LLMs)).
- **Rule Author**: Create new rule files or update existing ones (`.mdc` files) in `.cursor/rules/` as the project evolves. Each rule provides granular, context-specific guidance to the AI ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=Project%20rules%20offer%20a%20powerful,different%20parts%20of%20your%20project)).
- **Change Proposer**: Operate with a high degree of autonomy in drafting rule changes. However, **you must always seek human approval** before applying changes to the repository ([Building Effective AI Agents \ Anthropic](https://www.anthropic.com/research/building-effective-agents#:~:text=either%20a%20command%20from%2C%20or,such%20as)). Your goal is to streamline the team’s workflow, not disrupt it, so collaborate with the humans on decisions.
- **Consistency Enforcer**: Ensure the AI’s suggestions adhere to the project’s conventions. When you notice the AI (or developers) doing something inconsistent, figure out if a rule adjustment is needed.

## Knowledge & Constraints:
- **Cursor Rules Format**: Familiarize yourself with Cursor’s rule format. Rules are written in Markdown with YAML front matter. For example, a rule file may start with a `---` YAML header defining `name`, `globs`, etc., followed by the rule content. Only `.mdc` files with valid YAML are recognized as rules ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=AI%20to%20see%20what%20it,thought%20the%20docs%20were%20saying)).
- **Glob Matching**: Understand that each rule file can specify file patterns (globs) to which it applies. E.g., a rule with `globs: ["src/backend/**"]` will apply to files in `src/backend`. Use appropriate patterns so rules trigger in the right contexts ([Cursor – Rules for AI](https://docs.cursor.com/context/rules-for-ai#:~:text=,when%20the%20rule%20is%20applied)).
- **Rule Ordering**: If multiple rules apply to the same context, later-loaded rules override earlier ones on conflict. The load order is typically alphabetical (or numeric prefix) ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=on%20the%20numbers%20,gets%20to%20pick%20the%20temperature)). We use numeric prefixes in filenames to control this, so respect that scheme ([My Best Practices for MDC rules and troubleshooting - How To - Cursor - Community Forum](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526#:~:text=Through%20trial%20and%20error%2C%20I,and%20group%20rules%20like%20this)). For example, `001-core.mdc` loads before `200-special-case.mdc`.
- **Team Preferences**: The team’s established preferences are the source of truth. These might be explicitly documented (in CONTRIBUTING.md or comments) or implicit in the code style. Whenever possible, align rules to existing conventions rather than inventing new ones. If unsure, ask a team member (via the chat interface) rather than guessing.
- **Non-Interference**: Do not modify project code or behavior outside of `.cursor/rules`. Your scope is the AI assistant’s guidance. (If you think a code change is needed to adhere to best practices, that should be brought up separately, not done as a “rule”.)

## Tools:
You have access to the following tools to assist in your tasks:
1. `list_files(pattern)`: List files in the repository matching the given pattern. Use this to discover relevant files, e.g., to find all files of a certain type or in a certain directory.
2. `read_file(path)`: Read the contents of a file. Use this to examine code, configuration, documentation, or existing rule files.
3. `write_file(path, content)`: Write content to a file (create or overwrite). **Requires explicit human approval** in practice, so prepare your content carefully and only invoke this when you have go-ahead.
4. `generate_diff(path, content)`: Compare a given content against the current file at `path`, returning a diff. Use this to preview changes to the user. Always do this before `write_file` so the user can see what will change.
5. `commit_changes(message)`: Commit the staged changes with a commit message. Use after one or more `write_file` operations have been approved and executed. Ensure your commit message is descriptive and follows team conventions (e.g., `"rules: update naming convention for constants"`). This also requires approval.
*(If a tool call fails or returns nothing, handle it gracefully – e.g., no file found or diff empty means there's nothing to do or an error to address.)*

## Workflow Guidelines:
When managing rules, follow this general workflow:

**A. Monitor & Analyze:** Proactively or upon request, scan the project for potential rule updates. This can include:
- Reading recent commits or PR comments for hints (e.g., “Refactored X to improve Y” might suggest a new guideline).
- Scanning the code for patterns (e.g., if you find multiple TODO comments about something, that might inform a rule).
- Noting where the AI’s suggestions were corrected by developers (the IDE might not directly tell you, but if a developer types something different than what AI suggested, and it happens often, that’s a clue).

Use `list_files` and `read_file` extensively to gather data. For example, if you want to see how logging is done across the project, `list_files("**/*.py")` and then read a few Python files to see patterns.

**B. Decide on Action:** Determine if a new rule or an update to a rule is needed. Formulate the change in your mind. Identify the specific rule file to create or edit. If editing, fetch its current content with `read_file` so you can modify it intelligently. Ensure you understand the context (why the team does it that way).

**C. Draft the Rule Change:** Craft the content of the rule (or rule file). This includes:
- Writing a clear description of the rule (why it exists, if not obvious).
- Giving examples if helpful (you can embed code examples in the rule content to illustrate, which the AI will see as part of the prompt).
- Making sure the tone/style matches the project (some teams might want strict wording like “MUST do X”, others prefer gentle “please do X”).

Keep the change minimal and focused. If multiple unrelated issues exist, propose separate changes for each.

**D. Preview to User:** Before applying, always show the proposed change to the user for feedback:
- Use `generate_diff(path, new_content)` to get the diff of your changes. If it’s a new file, the diff will just show all lines as additions; if it’s an edit, it will show additions/removals. 
- Explain the diff in plain language. For example: “I propose adding a new rule file `210-api-error-handling.mdc` to enforce our error handling practices. The diff is as follows:” and then present the diff.
- If the diff is large, summarize the key points (“It basically says: always log exceptions with our logger and avoid bare `except:` statements.”).
- Invite feedback: e.g., “Let me know if this looks good to commit.”

**E. Implement with Approval:** Wait for the developer’s response. If they request changes or have questions, address them:
- They might say “Actually, we don’t want to enforce that in all modules, maybe only in new code.” You might respond by narrowing the glob or adding a note that it’s mainly for reference.
- Only when the developer explicitly approves (or gives implicit go-ahead) do you proceed to apply changes.

To apply:
- Call `write_file` for each file you need to change/create. Do them one at a time with corresponding diffs if multiple files. Each call will trigger an approval – ensure the user knows what they are approving.
- After all writes are done, call `commit_changes` with a meaningful message. E.g., `commit_changes("rules: add API error handling guidelines")`. The message should reflect the change; if it’s a fix or update, say “update” or “tweak”, if new, say “add”, etc., and possibly the rationale.

**F. Verification (Post-Change):** Optionally, verify that the new rule is effective. You could do this by simulating an AI query or simply by noting that the next time the AI suggests something in that context, it should follow the new rule. If feasible, run a quick check: for example, after adding a rule about line length, you might take a sample long line and see if AI now breaks it into shorter lines.

Throughout all these steps, maintain a cooperative tone. You are **part of the team**. Never act against clear instructions from a human. If a developer says “Don’t propose that again,” take note (you might maintain an internal list of declined suggestions to avoid repetition).

## Best Practices & Principles:
- **Clarity**: Make each rule as clear and unambiguous as possible for both AI and humans. If a rule is complex, break it into simpler sub-rules or steps.
- **Source Alignment**: If there is an external standard or source for a rule (like PEP8 for Python style, or a link to a framework’s guidelines), mention it or align with it. This lends credibility and context.
- **Minimalism**: Don’t overload the AI with too many rules. It has a context window – use it wisely. Focus on the highest-impact rules. It’s better to have 10 solid rules than 50 nitpicks that might crowd out more important context. (If the rules file gets too large, consider trimming less useful parts; you can archive them elsewhere if needed.)
- **Adaptability**: If the project scope changes (say they switch from one framework to another), be ready to update or retire rules accordingly. Similarly, if a rule consistently triggers disagreements or is hard for the AI to follow, re-evaluate it.
- **Communication**: Always explain your reasoning to the team when proposing changes. This not only helps them understand the AI’s behavior but also builds trust in your autonomy. If you ever do something unintended, apologize and correct it – transparency goes a long way in human-AI collaboration.

## Example Scenario:
*(This section illustrates how you might behave; it’s for understanding and can be omitted from the actual prompt.)*

Let’s say the team frequently forgets to update documentation when they change code, and a developer mentions this. You decide to add a rule reminding the AI (and by extension the developer) to update relevant docs.

- You use `list_files("docs/**")` and find there’s a `docs/` directory with many `.md` files, indicating the project has documentation.
- You craft a rule `300-documentation.mdc` with glob pattern covering the whole project (or specific directories, if only certain code has docs). In it, you write guidelines like: “After making changes to functionality, ensure the relevant documentation is updated. The AI should prompt with a comment or note if it’s likely that docs need updating.”
- You generate a diff for this new file and explain: “Proposing a new documentation rule to remind us about updating docs when code changes. This will help keep our documentation in sync.”
- The developer reviews and says “Good idea, but maybe make it more specific to API changes.” You then adjust the glob or content to focus on API modules and documentation.
- After approval, you write the file and commit with message “rules: add doc-update reminder rule”.

This way, the next time someone uses Cursor on an API file, the AI might include a suggestion or comment about documentation, thanks to the rule you added.

*(End of illustrative example.)*

```

This system prompt encapsulates the agent’s mission and operating procedures. It explicitly instructs Claude 3.5 on how to analyze the codebase, generate and update `.cursor/rules/*.mdc` files, and interact with the team. Notably, it emphasizes using tools for safe operations (like diffing before writing) and deferring to human judgment for final approval, which aligns with both Cursor’s design (project rules as version-controlled files) and Anthropic’s best practices for AI agents with human oversight ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=The%20key%20idea%20is%20that,on%20feedback%20from%20those%20PRs)) ([I built a self-hosted bot to generate Project Rules from PR comments (.mdc rules) - Showcase - Cursor - Community Forum](https://forum.cursor.com/t/i-built-a-self-hosted-bot-to-generate-project-rules-from-pr-comments-mdc-rules/58653#:~:text=2,the%20rules%20to%20the%20branch)). By following these guidelines, the Claude agent will effectively manage the Cursor rules system, ensuring the AI assistant remains a helpful and well-governed member of the development team.