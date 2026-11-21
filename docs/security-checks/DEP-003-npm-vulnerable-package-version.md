# ID and Title

- **ID:** DEP-003
- **Title:** NPM - Vulnerable Package Version
- **Why it matters**:

  An added or updated dependency may resolve to a version affected by a publicly disclosed vulnerability. The vulnerable behavior can occur when the application uses the package, independently of installation scripts.

  - **Real-world example: `fast-xml-parser` — CVE-2023-34104**
    - **Advisory:** GHSA-6w63-h3fj-q4vw, published June 6, 2023.
    - **Affected versions:** `>=4.1.3, <4.2.4`.
    - **Patched version:** `4.2.4`.
    - **Impact:** Crafted XML entity names can produce an inefficient regular expression and stall parsing, causing denial of service.
    - **Advisory severity:** High, CVSS 7.5.
    - **Reference:** Maintainer security advisory — Regex Injection via Doctype Entities.  
      https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-6w63-h3fj-q4vw
    - **Reference:** GitHub Advisory Database — CVE identifier, affected range, and patched version.  
      https://github.com/advisories/GHSA-6w63-h3fj-q4vw

- **Detection criteria**:

  - **Published vulnerability:** GitHub Advisory Database contains a reviewed, non-withdrawn security advisory for the dependency (`type: reviewed`, `withdrawn_at: null`).
  - **Package match:** The advisory's `vulnerabilities[].package` identifies the same npm package by `ecosystem` and `name`.
  - **Affected version:** The exact resolved version of an added or updated direct or transitive dependency falls within that package entry's `vulnerable_version_range`.

  ### References

  GitHub Docs — Global security advisories; lookup by `ecosystem` and `affects=package@version`, advisory status, and affected-version fields.

  https://docs.github.com/en/rest/security-advisories/global-advisories#list-global-security-advisories

- **Evidence**:

  - **Package and change:** Package name, exact resolved version, and the manifest or lockfile change, with file and line references. Cite the resolved dependency record rather than treating a declared version range as an installed version.
  - **Dependency path:** The path from the application to the affected direct or transitive dependency.
  - **Lookup evidence:** The queried npm package and version, source URL or API request, retrieval date, and the returned advisory excerpt or response.
  - **Advisory identity and status:** `ghsa_id`, `cve_id` when assigned, `html_url`, `type`, `withdrawn_at`, and `updated_at` from the retrieved record.
  - **Version comparison:** The matching package entry's `ecosystem`, `name`, and `vulnerable_version_range`; the application's resolved version; and the comparison result. Include `first_patched_version` when provided.
  - **Applicability:** Any verified usage conditions or mitigations relevant to the application. Distinguish affected-version evidence from confirmed exploitation.

- **Severity guidance:** Pending.

- **Safe and unsafe examples**:

  Hypothetical outputs for GHSA-6w63-h3fj-q4vw only.

  - **Safe: `fast-xml-parser@4.2.4`**

    ```text
    Package: fast-xml-parser@4.2.4
    Advisory: GHSA-6w63-h3fj-q4vw / CVE-2023-34104
    Affected range: >=4.1.3, <4.2.4
    Version match: No
    Result: No finding for this advisory.
    ```

  - **Unsafe: `fast-xml-parser@4.2.3`**

    ```text
    Package: fast-xml-parser@4.2.3
    Advisory: GHSA-6w63-h3fj-q4vw / CVE-2023-34104
    Affected range: >=4.1.3, <4.2.4
    Version match: Yes
    Result: Known vulnerable package version detected.
    Patched version: 4.2.4
    ```

- **False-positive limitations**:

  - **Incomplete lookup:** A failed lookup or missing resolved version is **Unverified**. A successful search with no match means no matching advisory was found in that source, not proof that the package is free of vulnerabilities.
  - **Unresolved version ranges:** A manifest range may allow both affected and unaffected versions. Use the resolved version before reporting a match.
  - **Usage conditions and mitigations:** An affected version does not prove exploitation in the application. For this advisory, the maintainer documents `processEntities: false` as a workaround.
  - **Advisory-specific results:** A version patched for one advisory may be affected by another. A non-match applies only to the advisory checked.
