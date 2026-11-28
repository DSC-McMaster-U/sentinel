# REL-003 · Remote artifact without a checksum

## Why it matters

Dockerfile `ADD` can fetch release artifacts over HTTP(S). A version in the URL still allows the server to return different bytes. Docker supports a reviewed SHA-256 checksum and fails the build if the downloaded bytes differ. [Dockerfile ADD reference](https://docs.docker.com/reference/dockerfile/#add---checksum)

## Detection and evidence

Inspect a changed shell-form `ADD` with one literal HTTP(S) source and a destination. Check instruction options for `--checksum=sha256:<64 hexadecimal digits>`. Report **medium** if the option is absent or its literal SHA-256 value is malformed. Skip unresolved variables, unsupported checksum algorithms, Git sources, local sources and ambiguous syntax. A checksum appearing in a comment or URL does not verify the artifact.

Cite the path, new-side instruction span and remote source. Describe the missing or malformed checksum and recommend pinning a trusted release digest. The [risky example](../../evaluation/fixtures/risky/release-add-unverified.json) expects one finding on line 2. The [safe example](../../evaluation/fixtures/safe/release-add-verified.json) supplies a literal checksum on the same instruction.

## Limitations

This deterministic check targets the download instruction. A later stage may independently verify the artifact before use. Human review can establish that ordering. A checksum pins bytes but cannot authenticate the initial digest. Archive extraction, shell downloads and artifact signing workflows fall outside this rule.
