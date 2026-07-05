<!-- MIT-licensed -->
# skillctl (npm wrapper)

This is a thin wrapper that allows you to install and run the `skillctl` Python package via npm or npx.

## Usage

```bash
npx skillctl --help
```

Or install globally:

```bash
npm install -g skillctl
skillctl --help
```

It simply checks if `skillctl` is available on your path, and if not, downloads the wheel from PyPI via `python3 -m pip install --user skillctl`.
