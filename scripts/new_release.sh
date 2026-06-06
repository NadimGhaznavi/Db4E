#!/bin/bash
# update_version.sh - Automated version update script for AI Hydra
#
# This script updates the version number across all relevant files in the AI Hydra project.
# It ensures consistency across pyproject.toml, Python packages, and documentation.
#
# Usage: ./update_version.sh <new_version>
# Example: ./update_version.sh 0.6.0

set -e  # Exit on any error

# ----- Project info -----
PROJECT_NAME="Db4E"
PROJECT_DIR="db4e"
DDEF_FILE="$PROJECT_DIR/constants/DDef.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ----- Function Definitions -----

# Check clean Git: Ensure working tree is clean before release flow starts
check_clean_git() {
    if [[ -n "$(git status --porcelain)" ]]; then
        print_error "Git working tree is not clean."
        echo ""
        git status --short
        echo ""
        print_error "Please commit or stash your changes before running this release script."
        exit 1
    fi

    print_success "Git working tree is clean"
}

# Ensure release starts from a feature branch
check_feature_branch() {
    local branch

    branch=$(git branch --show-current 2>/dev/null || true)

    if [[ -z "$branch" ]]; then
        print_error "Not currently on a named git branch. Are you in detached HEAD state?"
        exit 1
    fi

    if [[ "$branch" == "main" || "$branch" == "dev" || "$branch" == release/* ]]; then
        print_error "This script must be run from a feature branch."
        print_error "Current branch: $branch"
        exit 1
    fi

    if [[ "$branch" != feat/* && "$branch" != feature/* ]]; then
        print_error "Feature branch must be named feat/... or feature/..."
        print_error "Current branch: $branch"
        exit 1
    fi

    CURRENT_BRANCH="$branch"
    print_status "Git feature branch: $CURRENT_BRANCH"
}

commit_and_push_branch() {
    local commit_message=$1
    local branch

    if [[ -z "$commit_message" ]]; then
        print_error "No commit message provided to commit_and_push_branch"
        exit 1
    fi

    branch=$(git branch --show-current 2>/dev/null || true)

    if [[ -z "$branch" ]]; then
        print_error "Not currently on a named git branch. Cannot commit and push."
        exit 1
    fi

    if [[ -z "$(git status --porcelain)" ]]; then
        print_warning "No changes to commit on $branch"
    else
        print_status "Committing changes on $branch..."
        git add pyproject.toml "$DDEF_FILE" CHANGELOG.md
        git commit -m "$commit_message"
        print_success "✓ Committed changes on $branch"
    fi

    print_status "Pushing $branch..."
    git push -u origin "$branch"
    print_success "✓ Pushed $branch"
}

create_and_switch_branch() {
    local branch=$1

    if [[ -z "$branch" ]]; then
        print_error "No branch name provided to create_and_switch_branch"
        exit 1
    fi

    print_status "Creating and switching to $branch branch..."
    git checkout -b "$branch"
    print_success "✓ Created and switched to $branch branch"
}

# Execute a git merge
merge_branch() {
    local source_branch=$1
    local merge_message=$2

    if [[ -z "$source_branch" ]]; then
        print_error "No source branch provided to merge_branch"
        exit 1
    fi

    if [[ -z "$merge_message" ]]; then
        print_error "No merge message provided to merge_branch"
        exit 1
    fi

    print_status "Merging $source_branch into $(git branch --show-current)..."

    git merge --no-ff "$source_branch" -m "$merge_message"

    print_success "✓ Merged $source_branch"
}

# ----- Functions to print colored output -----
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

switch_to_branch() {
    local branch=$1

    if [[ -z "$branch" ]]; then
        print_error "No branch name provided to switch_to_branch"
        exit 1
    fi

    print_status "Switching to $branch branch..."
    git checkout "$branch"
    print_success "✓ Switched to $branch branch"
}

tag_and_push_release() {
    local version=$1
    local tag_message=$2
    local tag_name

    if [[ -z "$version" ]]; then
        print_error "No version provided to tag_and_push_release"
        exit 1
    fi

    if [[ -z "$tag_message" ]]; then
        print_error "No tag message provided to tag_and_push_release"
        exit 1
    fi

    tag_name="v$version"

    print_status "Creating release tag $tag_name..."
    git tag -a "$tag_name" -m "$tag_message"

    print_status "Pushing main and tag $tag_name..."
    git push origin main
    git push origin "$tag_name"

    print_success "✓ Pushed main and tag $tag_name"
}

# Function to update version in a file
update_file_version() {
    local file=$1
    local sed_script=$2
    local description=$3

    if [ -f "$file" ]; then
        print_status "Updating $description: $file"

        if sed -i.bak -E "$sed_script" "$file"; then
            rm -f "$file.bak"
            print_success "✓ Updated $file"
        else
            print_error "✗ Failed to update $file"
            return 1
        fi
    else
        print_warning "File not found: $file (skipping)"
    fi
}

# Function to update CHANGELOG.md with new release heading
update_changelog() {
    local version=$1
    local changelog_file="CHANGELOG.md"
    
    if [ ! -f "$changelog_file" ]; then
        print_warning "CHANGELOG.md not found (skipping changelog update)"
        return 0
    fi
    
    print_status "Updating CHANGELOG.md with release $version"
    
    # Get current date and time in the desired format
    local release_date=$(date '+%Y-%m-%d %H:%M')
    local release_heading="## [Release $version] - $release_date"
    
    # Create a temporary file for the updated changelog
    local temp_file=$(mktemp)
    
    # Process the changelog: add new release heading after [Unreleased]
    awk -v release_heading="$release_heading" '
    /^## \[Unreleased\]/ {
        print $0
        print ""
        print release_heading
        print ""
        next
    }
    { print }
    ' "$changelog_file" > "$temp_file"
    
    # Replace the original file
    if mv "$temp_file" "$changelog_file"; then
        print_success "✓ Updated CHANGELOG.md with release $version"
    else
        print_error "✗ Failed to update CHANGELOG.md"
        rm -f "$temp_file"
        return 1
    fi
}


# ----- End of functions -----

# Check if required arguments are provided
if [ $# -ne 3 ]; then
    print_error "Invalid number of arguments"
    echo "Usage: $0 <new_version> <release_comment> <new_feature_branch>"
    echo "Example: $0 0.15.20 \"v0.15.20 - DevOps Flow Release\" feat/newWidget"
    echo ""
    echo "Arguments:"
    echo "  new_version         Semantic version number, e.g. 0.15.20"
    echo "  release_comment     Git commit/tag message, e.g. \"v0.15.20 - DevOps Flow Release\""
    echo "  new_feature_branch  New feature branch to create after release, e.g. feat/newWidget"
    exit 1
fi

NEW_VERSION=$1
RELEASE_COMMENT=$2
NEW_FEATURE_BRANCH=$3

# Validate version format (basic check for X.Y.Z)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format: $NEW_VERSION"
    echo "Version must follow semantic versioning format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
    exit 1
fi

# Validate the branch format
if [[ "$NEW_FEATURE_BRANCH" != feat/* && "$NEW_FEATURE_BRANCH" != feature/* ]]; then
    print_error "New feature branch must be named feat/... or feature/..."
    print_error "Provided branch: $NEW_FEATURE_BRANCH"
    exit 1
fi

print_status "Updating $PROJECT_NAME version to $NEW_VERSION..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Get current pyproject version for comparison
CURRENT_VERSION=$(grep "version = " pyproject.toml | head -1 | sed 's/.*version = "\([^"]*\)".*/\1/')
print_status "Current version: $CURRENT_VERSION"
print_status "New version: $NEW_VERSION"

# Get current git branch
check_feature_branch

# Ensure the current git environment is clean
check_clean_git

read -p "Proceed with release $NEW_VERSION from feature branch '$CURRENT_BRANCH'? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Version update cancelled"
    exit 0
fi

echo ""
print_status "Starting version update process..."

# Switch to dev and merge in the current feature branch
switch_to_branch "dev"
merge_branch "$CURRENT_BRANCH" "Merge $RELEASE_COMMENT into dev"

# Create a new release branch
RELEASE_BRANCH="release/v$NEW_VERSION"
create_and_switch_branch "$RELEASE_BRANCH"

# Update pyproject.toml
update_file_version "pyproject.toml" \
    "s/version = \"[0-9]+\.[0-9]+\.[0-9]+\"/version = \"$NEW_VERSION\"/" \
    "primary version (pyproject.toml)"

# Update VERSION in db4e/constants/DDef.py
update_file_version "$DDEF_FILE" \
    "s/VERSION: Final\[str\] = \"[0-9]+\.[0-9]+\.[0-9]+\"/VERSION: Final[str] = \"$NEW_VERSION\"/" \
    "db4e/constants/DDef version"

# Update documentation conf.py
#if [ -f "docs/_source/conf.py" ]; then
#    print_status "Updating documentation version: docs/_source/conf.py"
#    sed -i.bak "s/release = '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*'/release = '$NEW_VERSION'/" docs/_source/conf.py
#    sed -i.bak "s/version = '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*'/version = '$NEW_VERSION'/" docs/_source/conf.py
#    rm -f docs/_source/conf.py.bak
#    print_success "✓ Updated docs/_source/conf.py"
#fi

# Update CHANGELOG.md with new release heading
update_changelog "$NEW_VERSION"

echo ""
print_success "Version update complete!"

# Verification
print_status "Verifying version consistency..."
echo ""
echo "=== Version Verification ==="

# Check pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo "📄 pyproject.toml:"
    grep "version.*=" pyproject.toml | head -1
fi

# Check DDef VERSION constant
if [ -f "$DDEF_FILE" ]; then
    echo "🐍 db4e/constants/DDef.py:"
    grep "DB4E_VERSION" db4e/constants/DDef.py | head -1
fi

# Check documentation
#if [ -f "docs/_source/conf.py" ]; then
#    echo "📚 docs/_source/conf.py:"
#    grep -E "(release|version) = " docs/_source/conf.py
#fi

# Check CHANGELOG.md
if [ -f "CHANGELOG.md" ]; then
    echo "📝 CHANGELOG.md:"
    grep -A 2 "## \[Unreleased\]" CHANGELOG.md | head -5
fi

echo ""

# Setup the release branch
commit_and_push_branch "$RELEASE_COMMENT"

# Switch to main
switch_to_branch "main"
# Merge in the new release
merge_branch "$RELEASE_BRANCH" "Merge $RELEASE_COMMENT into main"
# Tag the files and push out the new release
tag_and_push_release "$NEW_VERSION" "$RELEASE_COMMENT"

# Switch back to dev and merge release changes
switch_to_branch "dev"
merge_branch "$RELEASE_BRANCH" "Merge $RELEASE_COMMENT back into dev"
git push origin dev

# Create next feature branch
create_and_switch_branch "$NEW_FEATURE_BRANCH"

print_success "Release $NEW_VERSION completed successfully"
print_success "Now on new feature branch: $NEW_FEATURE_BRANCH"