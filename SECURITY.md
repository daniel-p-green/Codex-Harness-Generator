# Security

## Scope

The Codex Harness Generator generates configuration files (Markdown, JSON) for
Codex environments. It does not handle secrets, credentials, or authentication
tokens directly. The generated files define assistant behavior, permissions, and
routing rules -- they do not store or transmit sensitive data.

## Reporting Vulnerabilities

If you discover a security vulnerability in the Harness Generator or in the patterns it
generates, please report it by opening a GitHub issue or emailing the maintainers
directly. Include a description of the issue, steps to reproduce, and the potential
impact.

## Generated Permissions

The Harness Generator generates a `.codex/config.toml` file with allow and deny rules
tailored to the user's project. **Users should review these permissions before use**
to ensure they match their security requirements. In particular:

- Verify that deny rules cover destructive operations relevant to your environment.
- Verify that allow rules do not grant broader access than intended.
- Adjust permissions for any sensitive tools or directories specific to your project.
