# ID and Title

- **ID:** DEP-001
- **Title:** Unintended Package Installation - Package Typosquatting
- **Why it matters**:

  A person or an AI assistant may mistake a similarly named npm package for the intended package. Attackers can exploit this confusion by publishing malicious packages with names resembling legitimate libraries.

  - **Real-world example 1: `crossenv` (2017)**
    - **Intended package:** `cross-env`, the legitimate package being impersonated.
    - **Actual package:** `crossenv`, a separate npm package.
    - **Mismatch pattern:** Removing the hyphen produces a different package identifier that resembles the legitimate name.
    - **Observed outcome:** The malicious package exfiltrated environment variables. This does not establish how each user selected it.
    - **Reference:** npm's incident disclosure: https://blog.npmjs.org/post/163723642530/crossenv-malware-on-the-npm-registry

  - **Real-world example 2: Lookalike npm package campaign (2025)**
    - **Intended packages:** Impersonated legitimate packages included `typescript`, `nodemon`, and `zustand`.
    - **Actual packages:** Corresponding lookalikes included `typescriptjs`, `nodemonjs`, and `zustand.js`.
    - **Mismatch pattern:** Adding `js` or `.js` creates a separate identifier while preserving the recognizable library name.
    - **Observed outcome:** Socket reported malicious installation hooks and a credential-harvesting payload. Whether individual selections came from people or AI was not established.
    - **Reference:** Socket's campaign report: https://socket.dev/blog/10-npm-typosquatted-packages-deploy-credential-harvester

  - **Real-world example 3: `@async-mutex/mutex` (2025)**
    - **Intended package:** `async-mutex`, the legitimate package being impersonated.
    - **Actual package:** `@async-mutex/mutex`, a separate scoped npm package.
    - **Mismatch pattern:** Reusing the legitimate name as a scope can suggest an association that the identifier alone does not establish.
    - **Observed outcome:** Socket reported Solana private-key theft and an AI search summary presenting the malicious package as legitimate. The report does not establish that a victim installed it because of that summary.
    - **Reference:** Socket's incident report: https://socket.dev/blog/gmail-for-exfiltration-malicious-npm-packages-target-solana-private-keys-and-drain-victim-s

  These are historical impersonation examples. Name similarity, suffixes, and scopes alone do not establish maliciousness or a user's intended package.

- **Detection criteria**:

  Based on OpenSSF's **Verify Authenticity** and **Name Verification** guidance:

  - **Authorized source:** Verify that the package is the authentic distribution from the authorized source, rather than a personal or attacker-controlled fork presented as the original.
  - **Name and project link:** Check the package name and the link provided by the project's official website.
    - **Sentinel verification procedure:** Start from an independently verified project repository or official documentation and follow its package distribution link. Compare the destination's exact npm package identifier, including its scope, with the dependency being inspected.
    - Do not establish authenticity solely from website or repository links supplied by the package being inspected. If the project's official source cannot be independently verified, record the result as **Unverified**.
  - **Fork relationship:** Verify the repository's fork relationship on GitHub or GitLab.
  - **Foundation affiliation:** Check whether the project is affiliated with a foundation.
  - **Creation time and popularity:** Check the project's creation time and popularity.
  - **Similar names:** Check whether a similarly named package is more popular, which could indicate typosquatting.

  ### References

  OpenSSF — Concise Guide for Evaluating Open Source Software; Initial Assessment → Verify Authenticity; Adoption & Licensing → Name Verification.

  https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html

- **Evidence**:

  - **Authorized source:** Record the verified official source URL and how it identifies the package as an authorized distribution.
  - **Name and project link:** Record the package name and link provided by the official project website, alongside the name and link of the package being inspected.
  - **Fork relationship:** Record the repository URL associated with the package and the verified original/fork relationship.
  - **Foundation affiliation:** Record any verified foundation affiliation and the official source supporting it.
  - **Creation time and popularity:** Record the creation date, popularity metric and value, data source, and retrieval date.
  - **Similar names:** Record the comparison package name, the name similarities, and popularity values compared using the same metric and time period.

  For each item, record the observed facts and their sources. If the information cannot be verified, mark it as **Unverified**.

- **Severity guidance:** Pending.

- **Safe and unsafe examples**:

  These synthetic PR inputs follow `PullRequestInput` and contain unified diffs. Both explicitly intend to use the cross-env project. Source verification remains part of the check; the inputs do not contain pre-filled verdicts or source observations. The examples assess identity, not current malware or merge decisions.

  - **Safe change: `cross-env`**
    - **Input:** Add `cross-env` as a dependency in `package.json`.
    - **Verification:** Follow the creator-site link to the project repository, then check its installation guide and npm distribution link. They identify `cross-env`, matching the added dependency.
    - **Expected result:** No DEP-001 finding. This does not certify the package's overall safety.
    - **Fixture:** [DEP-001-cross-env-safe.json](../../evaluation/fixtures/safe/DEP-001-cross-env-safe.json)
    - **Expected output:** [DEP-001-cross-env-safe.json](../../evaluation/expected-findings/DEP-001-cross-env-safe.json)

  - **Unsafe change: `crossenv`**
    - **Input:** Add `crossenv` as a dependency in `package.json`.
    - **Verification:** The official distribution identifies `cross-env`; `crossenv` is a different package identifier with the hyphen removed.
    - **Expected result:** Flag the package identity mismatch with the selected name, official name, and source links. Do not infer current malware or a final approval/rejection decision.
    - **Fixture:** [DEP-001-cross-env-risky.json](../../evaluation/fixtures/risky/DEP-001-cross-env-risky.json)
    - **Expected output:** [Pending expected finding](../../evaluation/expected-findings/DEP-001-cross-env-risky.md)

  The safe expectation is an empty findings list. The risky expectation remains a Markdown note until severity and the required `SecurityFinding` fields are agreed. No custom output fields are defined here. The evaluation harness and fixed source-response integration are still pending.

- **False-positive limitations**:

  - **Intentional alternative selection:** A legitimate fork or alternative package may have been deliberately selected. A different identifier alone does not establish an unintended selection; repository context or approved exceptions may explain the choice.
  - **Official source unavailable:** Failure to verify the official source is not evidence of a package identity mismatch. Record **Unverified** rather than treating missing evidence as a confirmed mismatch.
