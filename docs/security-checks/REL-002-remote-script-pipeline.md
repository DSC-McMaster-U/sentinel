# REL-002 · Remote script piped to a shell

## Why it matters

A build that interprets a remote response as shell input gives the remote publisher control over that build step. TLS alone cannot protect against a compromised publisher. [OWASP software supply chain guidance](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html)

## Detection and evidence

In a changed shell-form Dockerfile `RUN`, recognize a literal HTTP(S) URL passed to `curl` writing to stdout or `wget -O -` (including `-qO-`). Require the next command in the same pipeline to be `sh` or `bash` reading stdin, optionally with `-s`. Resolve quoted literal arguments and backslash-newline continuations. Skip quoted pipes, comments, file-output downloads and shells that execute a named file or command string.

Report **high** for this direct execution path. Cite the path and new-side physical lines spanning the download and shell, and identify both commands. Recommend a vendored script or verification against a reviewed digest before execution. The [risky example](../../evaluation/fixtures/risky/release-dockerfile-latest-and-curl-bash.json) expects a finding on Dockerfile line 4. The [safe example](../../evaluation/fixtures/safe/release-dockerfile-digest-bump.json) has no pipeline.

## Limitations

Match only the specified shell syntax deterministically. A log message containing a pipe is ordinary text. Wrappers, computed commands, indirect pipelines, heredocs and non-POSIX shells require separate analysis. A reviewer can assess organizational controls over an internal URL without downloading it.
