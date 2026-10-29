name: Update README

on:
  # One click: Actions tab -> "Update README" -> Run workflow
  workflow_dispatch:
  # Automatic: every day at 07:00 IST
  schedule:
    - cron: "30 1 * * *"
  # Runs once when you first add these files
  push:
    paths:
      - "scripts/update_readme.py"
      - ".github/workflows/update-readme.yml"

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Refresh repository list
        run: python scripts/update_readme.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Commit changes
        run: |
          if git diff --quiet; then
            echo "Nothing to commit."
            exit 0
          fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git commit -am "Update repository list"
          git push
