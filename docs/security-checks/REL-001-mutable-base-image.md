# REL-001 · Mutable base image

## Why it matters

A registry can change which image a tag identifies. Rebuilding the same release commit can therefore introduce different base layers without a reviewed source change. [Docker build best practices](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions)

## Detection and evidence

Inspect each changed `FROM [--platform=…] image [AS stage]` instruction. For a literal external image with an omitted tag, an explicit `latest`, or any other tag, report **medium** unless the reference ends with a valid SHA-256 digest (64 hexadecimal digits after `@sha256:`). Exclude `scratch` and references to previously declared stage aliases. Use full head text to resolve stage names when patch context is insufficient. Skip unresolved build arguments and unsupported digest algorithms.

Cite the new Dockerfile path, instruction lines and image reference. Recommend a reviewed digest bump with a readable version tag. The [risky fixture](../../evaluation/fixtures/risky/release-dockerfile-latest-and-curl-bash.json) points to line 1. The [safe bump](../../evaluation/fixtures/safe/release-dockerfile-digest-bump.json) keeps the digest pin.

## Limitations

The rule is deterministic. A registry may enforce tag immutability outside the repository. A human can document that control. A valid digest establishes a content identity without establishing the publisher's trustworthiness.
