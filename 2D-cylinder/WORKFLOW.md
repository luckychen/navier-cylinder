# Development Workflow

This document describes how to work with the navier-cylinder project and push changes to GitHub.

## Git Repository Setup

✅ **Already configured when you clone:**
- **Local:** `<your-cloned-directory>/navier-cylinder`
- **Remote:** `https://github.com/luckychen/navier-cylinder`
- **Branch:** `main`

---

## Daily Workflow

### 1. Make Changes

```bash
cd navier-cylinder  # your cloned directory

# Edit files, add features, fix bugs
vim navier_simple.cpp
# or update scripts, documentation, etc.
```

### 2. Check Status

```bash
git status
```

This shows which files are modified, added, or deleted.

---

## 3. Stage Changes

```bash
# Stage all changes
git add -A

# Or stage specific files
git add navier_simple.cpp
git add README.md
```

---

## 4. Commit Changes

```bash
# Commit with a meaningful message
git commit -m "Add feature: implement higher-order elements"

# Or use interactive mode
git commit
```

**Commit message guidelines:**
- Start with a verb: "Add", "Fix", "Improve", "Refactor"
- Keep first line under 50 characters
- Add details in body (optional)

**Examples:**
```
git commit -m "Fix boundary condition application in momentum solver"
git commit -m "Add support for higher Reynolds numbers (Re > 1000)"
git commit -m "Improve mesh generation for better cylinder resolution"
```

---

## 5. Push to GitHub

```bash
# Push to remote
git push origin main

# Or simply (after first setup)
git push
```

This uploads your commits to GitHub.

---

## Full Workflow Example

```bash
# Navigate to project
cd navier-cylinder  # your cloned directory

# Check what changed
git status

# Add your changes
git add -A

# Commit with message
git commit -m "Improve solver stability at high Re"

# Push to GitHub
git push origin main

# Verify
git status  # Should show "Your branch is up to date with 'origin/main'"
```

---

## Useful Git Commands

### View History
```bash
# See recent commits
git log --oneline | head -10

# See what changed in last commit
git show HEAD

# See changes since last push
git log origin/main..HEAD
```

### Undo Changes
```bash
# Discard changes to a file (before staging)
git checkout -- filename.cpp

# Unstage a file (after git add)
git reset HEAD filename.cpp

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Branching (Optional - for large features)
```bash
# Create feature branch
git checkout -b feature/high-order-elements

# Make changes and commit
git add -A
git commit -m "Implement P3 elements"

# Push feature branch
git push origin feature/high-order-elements

# Create Pull Request on GitHub
# Then merge to main when ready
```

---

## Important Files Not to Commit

The following are automatically ignored (via `.gitignore`):

- **Build files:** `build/`, `*.o`, `*.a`
- **Generated meshes:** `*.mesh` (except in repo)
- **Results:** `*.dat`, `*.gf`, `*.png`
- **Cache:** `__pycache__/`, `*.pyc`

These are created during runs but won't be tracked in git.

---

## Collaboration Example

### If Working with Others

1. **Before starting work:**
   ```bash
   git pull origin main  # Get latest changes
   ```

2. **During work:**
   - Make commits frequently (every feature/fix)
   - Write clear commit messages
   - Push regularly: `git push origin main`

3. **If conflicts arise:**
   ```bash
   # Someone else changed a file you're working on
   git pull origin main  # This will show conflicts
   # Edit conflicted files
   git add resolved_files
   git commit -m "Resolve merge conflicts"
   git push origin main
   ```

---

## File Organization

```
navier-cylinder/  (your cloned directory)
├── navier_simple.cpp           ← Main solver (edit this for physics)
├── CMakeLists.txt              ← Build config (edit if adding files)
├── generate_cylinder_mesh.py   ← Mesh generation (edit for mesh changes)
├── analyze_results.py          ← Analysis tools (edit for new plots)
├── setup_environment.sh        ← Setup script (stable, rarely changed)
├── quick_test.sh               ← Test script (stable, rarely changed)
├── README.md                   ← User guide (update when making changes)
├── README_SETUP.md             ← Setup documentation
├── LICENSE                     ← License (don't change)
├── WORKFLOW.md                 ← This file
└── build/                      ← Generated (gitignored)
```

---

## Making Improvements

### Adding a New Feature

1. **Edit solver:**
   ```bash
   vim navier_simple.cpp
   ```

2. **Update CMakeLists.txt if needed:**
   ```bash
   vim CMakeLists.txt
   ```

3. **Test:**
   ```bash
   cd build && cmake .. && make -j4
   ./navier_simple -m ../cylinder_structured.mesh -t 0.1
   ```

4. **Update documentation:**
   ```bash
   vim README.md         # User-facing changes
   vim README_SETUP.md   # Technical details
   ```

5. **Commit and push:**
   ```bash
   git add -A
   git commit -m "Add feature: [describe feature]"
   git push origin main
   ```

### Fixing a Bug

1. **Identify the issue**
2. **Edit the file:**
   ```bash
   vim navier_simple.cpp
   ```
3. **Test the fix**
4. **Commit:**
   ```bash
   git commit -m "Fix: [describe issue and solution]"
   git push origin main
   ```

---

## Keeping Track of Your Work

### Track Progress with Tags

```bash
# Tag a stable version
git tag -a v1.1 -m "Version 1.1: Added higher-order elements"

# Push tags to GitHub
git push origin --tags

# View all tags
git tag -l
```

### Generate Changelog

```bash
# See all commits since last tag
git log v1.0..HEAD --oneline
```

---

## Troubleshooting

### "Permission denied" when pushing
```bash
# Make sure SSH key is configured
ssh -T git@github.com

# If issues, check key permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### "Merge conflict" when pulling
```bash
# Your changes conflict with remote
# Edit the conflicted file (marked with <<<<<<, ======, >>>>>>)
# Then:
git add conflicted_file
git commit -m "Resolve merge conflict"
git push origin main
```

### "Detached HEAD" state
```bash
# You're not on a branch, go back to main
git checkout main
```

---

## Remote Repository

**View remote:**
```bash
git remote -v
```

**Output:**
```
origin  git@github.com:luckychen/navier-cylinder.git (fetch)
origin  git@github.com:luckychen/navier-cylinder.git (push)
```

**Repository URL:** https://github.com/luckychen/navier-cylinder

---

## Quick Reference

```bash
# Daily workflow
git status                    # Check status
git add -A                    # Stage changes
git commit -m "Message"       # Commit
git push origin main          # Push to GitHub

# Before pulling latest
git pull origin main          # Get latest changes

# View history
git log --oneline | head -10  # See recent commits

# Undo mistakes
git reset --hard HEAD~1       # Undo last commit
git checkout -- file.cpp      # Discard local changes
```

---

## Need Help?

```bash
# Git help
git help [command]
git help push
git help commit

# Check status anytime
git status
git log --oneline
git remote -v
```

---

**Happy coding! 🚀**
