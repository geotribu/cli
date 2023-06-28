# Geotribot: application manifest

This page describes what's the Geotribot and what it does exactly.

## What's Geotribot and who's behind?

Geotribot is the name of a set of automated applications and account on different platforms: GitHub, Mastodon, Slack and Twitter.

It's related to the [Geotribu website](http://geotribu.fr/) and powered by the team behind, particularly Julien Moura ([Github](https://github.com/guts/), [Mastodon](https://mapstodon.space/@geojulien), [Twitter](https://twitter.com/geojulien/)).

## What it does

- it sends the comments on internal Slack channel for moderation
- it (re)posts some comments on social networks
- it perform fixes on Markdown syntax during Pull Requests in Geotribu new content workflow
- it creates the backup of website and CDN releases on GitHub

### What it does not

- it doesn't read content on platforms
- it never stores anything anywhere, it just processes the data

----

## Source code

Obviously, the code behind Geotribot is full open source:

- through the Geotribu CLI: <https://github.com/geotribu/cli/>
- through the Geotribu Ansible recipes: <https://github.com/geotribu/infra/tree/master/ansible>
