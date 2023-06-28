#! python3  # noqa: E265

# 3rd party
from frontmatter import YAMLHandler
from frontmatter.util import u as unicoder
from yaml import Dumper, dump


class IndentedDumper(Dumper):
    """Custom YAML Dumper designed to indent values.

    See:

        - https://stackoverflow.com/a/39681672/2556577
        - https://github.com/yaml/pyyaml/issues/234
    """

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        """Increase indent on keys values.

        Args:
            flow: _description_. Defaults to False.
            indentless: _description_. Defaults to False.

        Returns:
            _description_
        """
        return super().increase_indent(flow, False)


class IndentedYAMLHandler(YAMLHandler):
    """Frontmatter YAML handler using the IndentedDumper."""

    def export(self, metadata: dict, **kwargs):
        """Export metadata as YAML. This uses yaml.SafeDumper by default."""
        kwargs.setdefault("Dumper", IndentedDumper)
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("allow_unicode", True)
        kwargs.setdefault("indent", 4)

        metadata = dump(metadata, **kwargs).strip()

        return unicoder(metadata)  # ensure unicode
