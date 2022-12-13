# Contributing Guidelines

First off, thanks for considering to contribute to this project!

These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Git hooks

We use git hooks through [pre-commit](https://pre-commit.com/) to enforce and automatically check some "rules". Please install it before to push any commit.

See the relevant configuration file: `.pre-commit-config.yaml`.

## Code Style

Make sure your code *roughly* follows [PEP-8](https://www.python.org/dev/peps/pep-0008/) and keeps things consistent with the rest of the code:

- docstrings: [google-style](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html) is used to write technical documentation.
- formatting: [black](https://black.readthedocs.io/) is used to automatically format the code without debate.
- sorted imports: [isort](https://pycqa.github.io/isort/) is used to sort imports
- static analysis: [flake8](https://flake8.pycqa.org/en/latest/) is used to catch some dizziness and keep the source code healthy.

## Branching

The pattern is: `{category}/{slugified-description}`. Where:

- `category` is the type of work. Can be: `feature`, `bug`, `tooling`, `refactor`, `test`, `chore`, `release`, `hotfix`, `docs`, `ci`, `deploy` or `release-candidate`.
- `slugified-description` is the description of the work, slugified.

Example: `feature/authentication-logic`

### Special branches

- `main`: the main branch.
