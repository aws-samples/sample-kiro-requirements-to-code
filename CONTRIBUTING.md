# Contributing

Thank you for your interest in contributing to this reference!

## How to Contribute

### Adding a New Example

1. Create a folder under `examples/example-N-<name>/`
2. Include:
   - `sample-prd/product-requirements.md` — The starting PRD
   - `.kiro/steering/` — At least product-overview + technology-guidelines
   - `.kiro/specs/` — At least one feature fully decomposed with stories
   - `.kiro/hooks/` — At least one relevant hook
   - `.kiro/settings/mcp.json` — MCP configuration
3. Ensure the example demonstrates a different domain or architectural pattern than existing examples
4. Add a section to the root README describing the example

### Improving Documentation

- Fix typos, clarify confusing sections, add missing examples
- Keep language concise and prescriptive
- Ensure Mermaid diagrams render correctly on GitHub

### Adding Templates

- Templates should be generic (no domain-specific content)
- Use bracketed placeholders (`[LIKE-THIS]`) for values that need customization, so `grep -n '\['` finds everything left to fill in
- In YAML templates, quote bracketed placeholders (`"[LIKE-THIS]"`) so the file still parses before customization
- Include comments explaining when/why to use each section

## Guidelines

- Keep examples realistic but simple enough to understand quickly
- Don't include actual secrets, credentials, or proprietary information
- Test that Terraform examples pass `fmt` and `validate`
- Ensure hook JSON is valid and follows the schema — run `python3 templates/hooks/scripts/check-hook-schema.py <path>`
- Run `python3 .kiro/hooks/scripts/check-spec-integrity.py` inside any example you change; it must report zero errors

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Security Issue Notifications

If you discover a potential security issue in this project, we ask that you notify AWS/Amazon Security
via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting/).
Please do **not** create a public GitHub issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT-0 License.
