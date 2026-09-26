# Security Policy — doc-services

## Overview

`doc-services` provides document extraction to text and Markdown, AGPL-free OCR, and content-based privacy screening for local LLM pipelines and autonomous agents. Security in `doc-services` focuses on local-first processing, zero external network egress, strict licence compliance (AGPL avoidance), content data protection, and unprivileged user-mode execution.

## Security Architecture & Guarantees

### 1. Local-First & Zero Network Egress
- All extraction, parsing, OCR rendering, and privacy classification routines execute strictly locally.
- `doc-services` opens no network ports, transmits no telemetry, and makes zero outbound HTTP/network requests.

### 2. AGPL-Free Licence Integrity
- PDF rendering and rasterization are performed exclusively through `pypdfium2` (BSD-3-Clause / Apache-2.0).
- PyMuPDF (`fitz`, AGPL) and other copyleft libraries are strictly excluded from the package and optional dependencies.
- This constraint is continuously enforced by automated contract tests (`tests/test_no_agpl.py`), protecting downstream proprietary and permissive integrations from unintended copyleft infection.

### 3. Fail-Closed Content-Based Privacy Screening
- The built-in privacy classifier (`darf_weitergegeben_werden()`) inspects actual document contents (such as IBANs, Tax IDs, Social Security numbers, health records, private SSH keys, and API tokens) rather than relying solely on file names or paths.
- Default evaluation is **fail-closed**: RED and YELLOW classifications block dissemination unless explicitly unblocked by intentional configuration.
- Diagnostic reports mask sensitive patterns to avoid leaking secrets in log streams.

### 4. Non-Elevated Execution (`RunAsInvoker`)
- All extractors, OCR bridges, and classification routines operate entirely in standard user space without requiring root or administrator privileges.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, privacy leak, or licence entanglement in `doc-services`:

1. **Do not open a public issue.**
2. Report the vulnerability privately via GitHub Security Advisories at [https://github.com/ellmos-ai/doc-services/security/advisories](https://github.com/ellmos-ai/doc-services/security/advisories) or directly to the maintainer.
3. Include detailed steps to reproduce, affected files or document types, and observed behavior.
4. Maintainers acknowledge reports within **48 hours**, and coordinate fixes and verification prior to any disclosure.
