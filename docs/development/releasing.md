# Release workflow

1. Fill the `CHANGELOG.md` with the new version. You can write it manually or use the auto-generated release notes by Github:
    1. Go to [project's releases](https://github.com/geotribu/cli/releases) and click on `Draft a new release`
    1. In `Choose a tag`, enter the new tag
    1. Click on `Generate release notes`
    1. Copy/paste the generated text from `## What's changed` until the line before `**Full changelog**:...` in the CHANGELOG.md replacing `What's changed` with the tag and the publication date
1. Change the version number in `__about__.py`
1. Apply a git tag with the relevant version: `git tag -a 0.3.0 {git commit hash} -m "New awesome feature"`
1. Push tag to main branch: `git push origin --tags`

If things go wrong (failed CI/CD pipeline, missed step...), here comes the fix process:

```sh
git tag -d old
git push origin :refs/tags/old
git push --tags
```

And try again!
