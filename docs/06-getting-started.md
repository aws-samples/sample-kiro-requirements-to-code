# Getting Started

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| [Kiro IDE](https://kiro.dev) | The development environment |
| Node.js (with `npx` on PATH) | Runs MCP servers |
| Git | Version control |
| AWS CLI v2 | AWS deployments (if using infra examples) |
| Terraform >= 1.14 | Infrastructure as Code (if using infra examples) |

### Optional (for MCP integrations)

| Requirement | Purpose | Install |
|-------------|---------|---------|
| `uv` (Python) | AWS documentation/pricing MCP servers | `pip install uv` |
| Azure DevOps PAT | Work-item sync with ADO | Generate in ADO settings |
| GitHub Token | Work-item sync with GitHub Issues | Generate in GitHub settings |

---

## Quick Setup (5 minutes)

### Option 1: Start from an Example

1. Copy an example folder into your project:
   ```bash
   cp -r examples/example-1-saas-platform/.kiro your-project/.kiro
   ```

2. Edit the steering files to match your project:
   - `.kiro/steering/product-overview.md` — Your product vision
   - `.kiro/steering/technology-guidelines.md` — Your tech stack
   - `.kiro/steering/coding-standards.md` — Your conventions

3. Configure MCP servers in `.kiro/settings/mcp.json`

4. Open your project in Kiro and start a conversation:
   ```
   "Here's our product requirements. Help me set up the spec structure."
   ```

### Option 2: Start from Templates

1. Create the `.kiro/` structure in your project:
   ```
   your-project/
   └── .kiro/
       ├── steering/
       ├── hooks/
       ├── specs/
       └── settings/
   ```

2. Copy templates from `templates/` into the appropriate directories — steering, specs,
   and hooks go under `.kiro/`; the CI workflows in `templates/workflows/` go to
   `.github/workflows/` (see [templates/workflows/README.md](../templates/workflows/README.md))

3. Fill in the bracketed placeholders — `grep -rn '\[' .kiro/steering/` finds what's left

4. Add your MCP configuration

---

## First Conversation: PRD Intake

Once Kiro is set up, start the decomposition process:

### Step 1: Share Your PRD

```
Here's our Product Requirements Document:

[paste your PRD or reference a file]

Help me:
1. Identify the major epics (3-5 capability areas)
2. Create a product-overview.md steering file
3. Create a technology-guidelines.md steering file
4. Suggest which epic to start with
```

### Step 2: Create Your First Feature

```
Let's decompose Epic 1 into features.

We have:
- [X] weeks for this PI
- [N] engineers
- [Key constraints or dependencies]

What features should we target?
```

### Step 3: Create Stories

```
Create stories for Feature [name].

Design decisions:
- [Key decision 1]
- [Key decision 2]

Team:
- [Person 1]: [focus area]
- [Person 2]: [focus area]

Sprint capacity: [N] PD per sprint
```

### Step 4: Implement Your First Story

```
I'm starting story [ref]. Let's discuss the implementation approach.

I'm thinking:
- [Approach idea 1]
- [Approach idea 2]

What do you think?
```

---

## MCP Server Configuration

### Minimal Setup (no external integrations)

```json
{
  "mcpServers": {}
}
```

Spec-driven development works without any MCP servers. You just won't have bidirectional sync with a work-item tracker.

### With Azure DevOps

```json
{
  "mcpServers": {
    "azureDevOps": {
      "command": "npx",
      "args": ["-y", "@tiberriver256/mcp-server-azure-devops@0.1.54"],
      "env": {
        "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/YOUR-ORG",
        "AZURE_DEVOPS_AUTH_METHOD": "pat",
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}",
        "AZURE_DEVOPS_DEFAULT_PROJECT": "Your Project"
      },
      "autoApprove": ["get_work_item", "search_work_items"]
    }
  }
}
```

Auto-approve only read operations. Write tools (`create_work_item`, `update_work_item`)
stay on manual approval so every tracker mutation gets your explicit sign-off — see the
sync principles in [05-work-item-sync-guide.md](05-work-item-sync-guide.md).

### With GitHub

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github@2025.4.8"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "autoApprove": ["get_issue", "list_issues"]
    }
  }
}
```

As with Azure DevOps, keep `create_issue` and `update_issue` out of `autoApprove`.

### With AWS Documentation (recommended)

```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@1.2.5"],
      "env": { "FASTMCP_LOG_LEVEL": "ERROR" },
      "autoApprove": ["search_documentation", "read_documentation"]
    }
  }
}
```

### Pinned server versions

Every snippet above names an exact package version (`pkg@x.y.z`) rather than
`@latest` or a bare package name. An MCP server runs on your machine with your
credentials, and `npx -y pkg` / `uvx pkg@latest` installs whatever the registry
serves at the moment Kiro starts it, so an unpinned entry turns a compromised
or typosquatted release into code execution on the next launch. To refresh a
pin, look up the current version (`npm view <pkg> version`, or the PyPI project
page for `uvx` packages), read the changelog, and update the string in
`mcp.json`; the `-y` flag only suppresses the npx install prompt and is safe to
keep.

Two notes on the specific packages:

- `@modelcontextprotocol/server-github` is archived upstream and marked
  deprecated on npm ("no security guarantees"); the maintained successor is
  the Go-based [`github/github-mcp-server`](https://github.com/github/github-mcp-server).
  The snippets keep the npm package because its tool names match the rest of
  these docs; plan a migration before relying on it.
- Do not add `get_file_contents` to the GitHub server's `autoApprove`. It
  returns any file from any repository the token can see, so a prompt-injected
  agent could read source and secrets without a confirmation prompt. Keep
  auto-approval to the issue and PR listing tools shown.

---

## Verify Your Setup

### Checklist

- [ ] `.kiro/steering/product-overview.md` exists with your product context
- [ ] `.kiro/steering/technology-guidelines.md` exists with your constraints
- [ ] `.kiro/settings/mcp.json` is configured (even if empty)
- [ ] Kiro loads without errors
- [ ] Start a conversation — Kiro references your steering content in its responses
- [ ] (Optional) MCP servers show connected in the Kiro sidebar

### Test the Workflow

1. Ask Kiro: *"What do you know about our project?"* — It should summarize your steering files
2. Ask Kiro: *"Create a sample feature spec for testing"* — It should use the correct folder structure
3. If using tracker integration: *"Can you read work item [ID]?"* — Confirms connectivity

---

## Next Steps

| Goal | Read |
|------|------|
| Understand the full process | [01-process-guide.md](01-process-guide.md) |
| Learn to decompose a PRD | [02-prd-decomposition-guide.md](02-prd-decomposition-guide.md) |
| Write better steering files | [03-steering-guide.md](03-steering-guide.md) |
| Set up quality automation | [04-hooks-guide.md](04-hooks-guide.md) |
| Configure tracker sync | [05-work-item-sync-guide.md](05-work-item-sync-guide.md) |
| See a full worked example | [examples/example-1-saas-platform/](../examples/example-1-saas-platform/) |
