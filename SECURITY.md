# Security Policy

## Scope

mythical-skills is a content repository: markdown skill procedures plus two
small CI check scripts. It ships no runtime code into consuming deployments.
The security surface that matters here is the **content** itself:

- skill text that would instruct an agent to exfiltrate data, bypass its
  authority model, or take destructive action;
- skill text that grants authority a skill must not grant (permission to push,
  merge, spawn, or override without external authorization);
- leaked secrets, tokens, personal data, or private infrastructure details in
  any tracked file.

## Reporting a vulnerability

**Use GitHub private vulnerability reporting.** On this repository, open the
**Security** tab and choose **Report a vulnerability** — that opens a private
advisory visible only to you and the maintainers.

Do not open a public issue, discussion, or pull request for anything that could
be exploited before it is fixed.

Include the file path, the concerning text, and why you believe it is
exploitable. You should receive an acknowledgment within a few business days.

## Supported versions

Only the `main` branch is maintained. There are no versioned security
backports for a content repository; fixes land on `main`.
