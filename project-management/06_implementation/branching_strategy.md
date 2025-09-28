# Branching Strategy

## Document Information
**Project**: [Project Name]  
**Version**: [Version]  
**Date**: [Date]  
**Tech Lead**: [Name]

## Branching Model
**Strategy**: [GitFlow/GitHub Flow/GitLab Flow]

## Branch Types

### Main Branches
- **main/master**: Production-ready code
- **develop**: Integration branch for features

### Supporting Branches
- **feature/**: New features
- **hotfix/**: Critical production fixes
- **release/**: Prepare new releases
- **bugfix/**: Non-critical bug fixes

## Branch Naming Conventions

| Branch Type | Format | Example |
|-------------|--------|---------|
| Feature | `feature/[ticket-id]-[description]` | `feature/PROJ-123-user-auth` |
| Hotfix | `hotfix/[ticket-id]-[description]` | `hotfix/PROJ-456-security-fix` |
| Release | `release/[version]` | `release/1.2.0` |
| Bugfix | `bugfix/[ticket-id]-[description]` | `bugfix/PROJ-789-ui-issue` |

## Workflow Process

### Feature Development
1. Create feature branch from `develop`
2. Implement feature
3. Create pull request to `develop`
4. Code review and approval
5. Merge to `develop`

### Release Process
1. Create release branch from `develop`
2. Final testing and bug fixes
3. Merge to `main` and tag
4. Merge back to `develop`

### Hotfix Process
1. Create hotfix branch from `main`
2. Implement fix
3. Merge to `main` and tag
4. Merge back to `develop`

## Branch Protection Rules

### Main Branch
- [ ] Require pull request reviews
- [ ] Dismiss stale reviews
- [ ] Require status checks
- [ ] Require up-to-date branches
- [ ] Restrict push access

### Develop Branch  
- [ ] Require pull request reviews
- [ ] Require status checks

## Commit Standards
- Use conventional commit format
- Include ticket/issue number
- Keep commits atomic and focused
- Write clear commit messages

## Merge Strategies
- **Feature branches**: Squash and merge
- **Release branches**: Merge commit
- **Hotfix branches**: Merge commit
