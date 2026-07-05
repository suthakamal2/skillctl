<!-- MIT-licensed -->
# skillctl Homebrew Tap

This directory contains the Homebrew formula for installing `skillctl`.

## Usage

To install via this formula:

```bash
brew tap suthakamal2/tap
brew install suthakamal2/tap/skillctl
```

## Creating the Tap Repository

1. Create a new GitHub repository named `homebrew-tap` under the `suthakamal2` organization/user.
2. The repository URL should be `https://github.com/suthakamal2/homebrew-tap`.
3. Copy `skillctl.rb` into the root of that repository.

## Publishing and Bumping Versions

You can bump the formula on each release using a GitHub Actions workflow that runs `brew bump-formula-pr`:

```bash
brew bump-formula-pr --url=https://files.pythonhosted.org/packages/source/s/skillctl/skillctl-NEW_VERSION.tar.gz skillctl
```

## Auditing

Before committing changes to the formula, audit it using:
```bash
brew audit --strict --new packages/skillctl/distribution/homebrew/skillctl.rb
```
