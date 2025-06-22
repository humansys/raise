# Atlassian Guidelines for Commit Messages and Issue Linking

## Key Principles

1. **Issue Key Format**
   - Must be in capital letters (e.g., "RAISE-123" not "raise-123")
   - Must be placed at the start of the commit message
   - Must be properly formatted with project key and issue number

2. **Basic Commit Message Structure**
   ```
   <ISSUE_KEY> <summary of commit>
   ```
   Example: `RAISE-123 Add session analysis framework`

3. **Smart Commits Syntax**
   ```
   <ISSUE_KEY> #<COMMAND> <arguments> #<COMMAND> <arguments>
   ```
   Example: `RAISE-123 #time 2h 30m Add session analysis framework #comment Implemented initial version`

## Best Practices

1. **Issue Linking**
   - Include the issue key at the beginning of the commit message
   - Use proper capitalization for automatic linking
   - Multiple issues can be referenced using spaces between keys

2. **Branch Naming**
   - Include the issue key in the branch name
   - Format: `<ISSUE_KEY>-<descriptive-name>`
   - Example: `RAISE-123-session-analysis`

3. **Pull Requests**
   - Include the issue key in the PR title
   - Ensure the source branch name includes the key
   - Link related issues in the PR description

4. **Related Work Items**
   - Parent/Child relationships can be indicated using multiple keys
   - Example: `RAISE-123 RAISE-124 Implement shared components`

## Commands for Smart Commits

1. **Comment**
   ```
   <ISSUE_KEY> #comment <comment_text>
   ```

2. **Time Tracking**
   ```
   <ISSUE_KEY> #time <value>w <value>d <value>h <value>m
   ```

3. **Transitions**
   ```
   <ISSUE_KEY> #<transition_name> <comment>
   ```

## Integration Features

1. **Automatic Linking**
   - Commits are automatically linked when using correct issue key format
   - Links appear in the Development panel of the issue
   - Build and deployment information is tracked when keys are used

2. **Work Item Updates**
   - Status changes can be triggered via commits
   - Time tracking can be logged directly
   - Comments can be added to issues

## Common Mistakes to Avoid

1. **Format Errors**
   - Using lowercase issue keys
   - Missing hyphen between project and issue number
   - Incorrect issue key format

2. **Content Issues**
   - Not putting the issue key at the start of the message
   - Including multiple commands without proper spacing
   - Using invalid transition names

## Examples of Good Commit Messages

1. Simple Issue Link:
   ```
   RAISE-123 Add session analysis framework
   ```

2. Multiple Issues:
   ```
   RAISE-123 RAISE-124 Implement shared components and tests
   ```

3. Smart Commit with Multiple Commands:
   ```
   RAISE-123 #time 2h #comment Completed session analysis implementation #done
   ```

4. Feature Branch Commit:
   ```
   RAISE-123 feat(cursor-rules): implement session analysis framework
   ```

## Additional Considerations

1. **Character Limits**
   - Maximum commit message length: 8,000 characters
   - Keep first line under 72 characters for readability

2. **Visibility**
   - Only linked commits appear in Jira Activity Stream
   - Links may take a few minutes to appear after push

3. **Project Renaming**
   - System supports old issue keys after project rename
   - Both old and new keys will work for linking 