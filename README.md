# uribo.github.io

Personal research website of Shinya Uryu — **Human × Environment × Information**. Built with [Quarto](https://quarto.org), deployed to GitHub Pages.

- Contributor / agent instructions: [AGENTS.md](AGENTS.md)
- Architecture and build pipeline: [docs/architecture.md](docs/architecture.md)
- Content metadata schemas: [docs/content-model.md](docs/content-model.md)

```sh
quarto preview                # local preview
uv run scripts/validate.py    # metadata validation
quarto render                 # full build
```
