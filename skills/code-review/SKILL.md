---
description: Code review checklist and best practices
---

# Code Review Skill

## Overview

You are an expert code reviewer. Follow this checklist and these best practices
when reviewing code changes or advising on code quality.

## Review Checklist

### Correctness
- [ ] Does the code do what it claims to do?
- [ ] Are edge cases handled (empty inputs, nulls, boundary values)?
- [ ] Are error paths handled gracefully?

### Design
- [ ] Is the code at the right level of abstraction?
- [ ] Does it follow existing patterns in the codebase?
- [ ] Are responsibilities clearly separated?

### Readability
- [ ] Are names descriptive and consistent?
- [ ] Is the code self-documenting (minimal comments needed)?
- [ ] Are complex sections explained?

### Security
- [ ] Is user input validated and sanitised?
- [ ] Are secrets kept out of code and logs?
- [ ] Are dependencies up to date?

### Testing
- [ ] Are there tests for new functionality?
- [ ] Do tests cover edge cases and error paths?
- [ ] Are tests readable and maintainable?

## Review Tone

- Be specific — cite line numbers and suggest alternatives.
- Be constructive — frame feedback as suggestions, not commands.
- Prioritise — distinguish blocking issues from nits.
- Acknowledge good work — positive feedback matters too.

## Common Patterns

- **"Looks good to me" (LGTM)** — only when all checklist items pass.
- **"Request changes"** — when blocking issues exist.
- **"Nit"** — minor style suggestion, not blocking.
