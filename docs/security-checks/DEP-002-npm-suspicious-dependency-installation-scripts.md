# ID and Title

- **ID:** DEP-002
- **Title:** NPM - Suspicious Dependency Installation Scripts
- **Why it matters**:

  npm supports installation lifecycle scripts, including `preinstall`, `install`, and `postinstall`. The following incidents used installation hooks to execute malicious code.

  - **Real-world example 1: ESLint package compromise (2018)**
    - **Affected packages:** `eslint-scope@3.7.2` and `eslint-config-eslint@5.0.2`, published through a compromised maintainer account.
    - **Installation entry point:** An added `postinstall` hook invoked `node ./lib/build.js`.
    - **Execution path:** The loader downloaded code from Pastebin and passed the response to `eval`. The preserved remote payload read the user's `.npmrc` and transmitted its contents to external services.
    - **Dependency relevance:** `eslint-scope` was a dependency of popular development tools.
    - **Actual discovery:** The initial reporter investigated an installation error and reported the suspicious loader.
    - **Reference:** ESLint — Official incident postmortem.  
      https://eslint.org/blog/2018/07/postmortem-for-malicious-package-publishes/
    - **Reference:** Henry Zhu — Preserved attack code linked by the postmortem.  
      https://gist.github.com/hzoo/51cb84afdc50b14bffa6c6dc49826b3e
    - **Reference:** eslint-scope — Original installation-error report and suspicious loader, issue #39.  
      https://github.com/eslint/eslint-scope/issues/39

  - **Real-world example 2: `eslint-config-prettier` compromise (2025)**
    - **Analyzed version:** SafeDep analyzed `9.1.1`. The initial community report separately compared `10.1.5` with `10.1.7`.
    - **Installation entry point:** An added `install` hook invoked `node install.js`.
    - **Execution path:** The release added `install.js` and `node-gyp.dll`. The JavaScript used split strings to construct a process-launch call that loaded the bundled DLL through Windows `rundll32`.
    - **Reported outcome:** SafeDep identified the DLL as a malware payload.
    - **Actual discovery:** The community questioned unexpected releases and used package diffs to identify the added installation script, DLL and suspicious launch code.
    - **Reference:** eslint-config-prettier — Original report and package diffs, issue #339.  
      https://github.com/prettier/eslint-config-prettier/issues/339
    - **Reference:** SafeDep — Version diff and DLL launcher analysis.  
      https://safedep.io/blog/eslint-config-prettier-major-npm-supply-chain-hack

- **Detection criteria**:

  - **Scope:** Newly added or updated dependencies, including transitive dependencies, at the versions resolved by the application.
  - **Script lookup:** For registry packages, inspect `npm view <package>@<version> scripts` for hooks applicable to the installation context. Compare with the previous version when available.
  - **When a hook is found:** Read its referenced files in the matching package artifact without executing them. Follow further commands, files, binaries, and download targets. Compare execution targets as well as the hook command.
  - **When no hook is shown:** Check the package artifact for implicit installation behavior, such as `binding.gyp` triggering the default `node-gyp rebuild`. An empty registry result alone does not establish the absence of installation execution.
  - **Child dependencies:** Use the application's resolved dependency tree to identify child packages and inspect their installation scripts and execution targets in the same way, whether or not the parent has a hook.
  - **Case-backed behavior:** Look for the behaviors documented above: downloaded code passed to `eval`, `.npmrc` contents sent externally, or an obscured launcher invoking a bundled DLL through `rundll32`.
  - **Unresolved targets:** If a referenced file, binary's behavior, or downloaded payload cannot be inspected, record the unverified part of the execution path.

  ### References

  npm CLI v12 — npm view; version-specific registry field lookup.

  https://docs.npmjs.com/cli/v12/commands/npm-view/#description

  npm CLI v12 — Scripts; installation lifecycle and implicit installation behavior.

  https://docs.npmjs.com/cli/v12/using-npm/scripts/#life-cycle-scripts

  npm CLI v12 — package-lock.json; resolved dependency tree.

  https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json/#description

- **Evidence**:

  - **Package and change:** Package name, exact resolved version, artifact source, and the manifest or lockfile diff showing the addition or update. Include the previous version when available.
  - **Dependency path:** The direct or transitive dependency path from the application to the affected package, supported by the resolved dependency tree.
  - **Installation entry point:** The version-specific script query and its output, together with the hook name and command in the package's `package.json`. For implicit installation behavior, cite the triggering package file and applicable npm behavior.
  - **Execution path:** File paths, line numbers, and code excerpts connecting the installation entry point to subsequent commands, files, binaries, or download targets.
  - **Suspicious behavior:** The specific operation and its inputs or destinations that support the finding, with the relevant code or artifact evidence. Include the before-and-after difference when available.
  - **Evidence gaps:** Any referenced target or behavior that could not be inspected, and where the verified execution path ends.

- **Severity guidance:** Pending.

- **Safe and unsafe examples**:

  - **Safe: `eslint-config-prettier@10.1.5`**

    **Command:**

    ```powershell
    npm.cmd view eslint-config-prettier@10.1.5 scripts dependencies optionalDependencies peerDependencies --json --registry=https://registry.npmjs.org
    ```

    **Output:**

    ```json
    {
      "eslint": ">=7.0.0"
    }
    ```

    **Package archive inspection output:**

    ```json
    {
      "package": "eslint-config-prettier",
      "version": "10.1.5",
      "tarball": "https://registry.npmjs.org/eslint-config-prettier/-/eslint-config-prettier-10.1.5.tgz",
      "integrity_verified": true,
      "scripts": null,
      "dependencies": null,
      "optionalDependencies": null,
      "peerDependencies": {
        "eslint": ">=7.0.0"
      },
      "binding.gyp": false,
      "install.js": false,
      "node-gyp.dll": false
    }
    ```

  - **Unsafe: `eslint-config-prettier@10.1.7`**

    **Command:**

    ```powershell
    npm.cmd view eslint-config-prettier@10.1.7 scripts --json --registry=https://registry.npmjs.org
    ```

    **Hypothetical output:**

    ```json
    {
      "install": "node install.js"
    }
    ```

    **Published package diff excerpts:**

    ```diff
    +  "scripts":{
    +    "install":"node install.js"
    +  },
    ```

    ```diff
    +    "install.js",
    +    "node-gyp.dll",
    ```

- **False-positive limitations**:

  - **Legitimate installation tasks:** Installation hooks may build native modules or prepare platform-specific binaries. A hook, download, or binary execution alone does not establish malicious behavior.
  - **Legitimate updates:** A newly added hook or executable alone does not establish malicious behavior. Check whether the change supports the package's functionality.
  - **Unverified code:** If remote code or a binary cannot be inspected, mark the relevant behavior as **Unverified**. Missing evidence is not evidence of malicious behavior.
