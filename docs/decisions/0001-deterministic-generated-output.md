# 0001. Deterministic Generated Output

## Status

Accepted

## Context

Operational documentation is often reviewed in pull requests and maintained over time. Non-deterministic output makes reviews noisy.

## Decision

Generated artifacts should be deterministic for the same repository state and tool version.

## Consequences

- Scanner output should be sorted where practical.
- Templates should avoid timestamps unless explicitly requested.
- Future report formats should preserve stable keys and ordering.
