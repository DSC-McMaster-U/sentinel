# Security Policy

Sentinel is a security tool, so we take vulnerabilities in our own code seriously.

## Supported Versions

Sentinel is in early development. Only the latest code on the `main` branch is supported.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues, pull requests, or Discord.**

Instead, report them privately using GitHub Security Advisories:

1. Go to the [Security tab](https://github.com/DSC-McMaster-U/sentinel/security) of this repository.
2. Click **Report a vulnerability** ([direct link](https://github.com/DSC-McMaster-U/sentinel/security/advisories/new)).
3. Include as much detail as you can:
   - A description of the issue and its potential impact
   - Steps to reproduce or a proof of concept
   - Affected files, endpoints, or components
   - Any suggested fix, if you have one

## What to Expect

- We aim to acknowledge your report within **3 days**.
- We will keep you updated as we investigate and work on a fix.
- Once resolved, we're happy to credit you in the advisory unless you prefer to stay anonymous.

## Contributor Reminders

- Never commit secrets, API keys, tokens, or credentials. Use environment variables and `.env` files, which must not be committed.
- If you accidentally commit a secret, tell a maintainer immediately so it can be rotated. Deleting the commit is not enough.
