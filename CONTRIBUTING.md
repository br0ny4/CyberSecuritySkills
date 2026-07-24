# Contributing to CyberSecuritySkills

Thank you for contributing to the world's largest cybersecurity AI skill library.

## Development Setup

```bash
git clone https://github.com/br0ny4/CyberSecuritySkills.git
cd CyberSecuritySkills
pip install -r requirements.txt
pip install pytest pytest-cov ruff
```

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert` `security`

**Scopes**: `scanner` `mcp` `adapter` `framework` `schema` `integration` `docs` `ci` `deps` `skills`

### Examples

```
feat(scanner): add CS4 prompt injection detection patterns
fix(mcp): resolve nmap sandbox parameter validation
security(adapter): patch command injection in trae adapter
docs(readme): update ATT&CK v19.1 mapping table
```

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production releases |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `security/*` | Security patches |

## Pull Request Process

1. Create a feature branch from `develop`
2. Implement changes with tests
3. Run validation:
   ```bash
   pytest tests/ --cov=. -v          # Unit tests
   python scanners/cs4_scan.py --all  # Security scan
   python scripts/compliance_checker.py  # Schema validation
   ruff check .                       # Lint
   ```
4. Submit PR to `develop` using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
5. PR checks must pass: CI (tests + security scan + lint + commitlint)

## Adding New Skills

1. Place skill in appropriate `skills/<domain>/` directory
2. Follow the [unified skill schema](schema/unified-skill.schema.json)
3. Run `python scripts/index_generator.py` to update the index
4. Run `python scanners/cs4_scan.py --file skills/<domain>/<skill>.md`
5. Submit PR

## Code Style

- Python 3.10+, type hints recommended
- Follow PEP 8, enforced via `ruff`
- 120 char line limit
- Docstrings for public APIs

## Community

- Report bugs via [GitHub Issues](https://github.com/br0ny4/CyberSecuritySkills/issues)
- Discuss features in [Discussions](https://github.com/br0ny4/CyberSecuritySkills/discussions)
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
