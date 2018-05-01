from __future__ import unicode_literals

import sys

import lektor.pluginsystem
import lektor.types
import markupsafe
import six

from .markdown import markdown_to_html, TutorialRenderer


class TutorialMarkdown(object):
    """Representation of a Markdown object.
    """
    def __init__(self, source):
        self.source = source

    def __bool__(self):
        return bool(self.source)

    def __getattr__(self, key):
        if key in ['_html', '_styles']:
            self._html, self._styles = markdown_to_html(
                self.source, renderer_cls=TutorialRenderer,
            )
            return getattr(self, key, '')
        return super(TutorialMarkdown, self).__getattr__(key)

    def __str__(self):
        return self.html

    # Python 2 compatibility.
    if six.PY2:
        __nonzero__ = __bool__
        __unicode__ = __str__

        def __str__(self):
            return self.__unicode__().encode(sys.getdefaultencoding())

    def __html__(self):
        return markupsafe.Markup(self.html)

    @property
    def html(self):
        return self._html

    @property
    def style_tag(self):
        return markupsafe.Markup('<style>{}</style>'.format(self._styles))


class TutorialMarkdownDescriptor(object):
    """Describes the Markdown object to the type.
    """
    def __init__(self, source):
        self.source = source

    def __get__(self, obj, type=None):
        return TutorialMarkdown(self.source)


class TutorialMarkdownType(lektor.types.Type):

    widget = 'multiline-text'

    def value_from_raw(self, raw):
        if raw.value is None:
            return raw.missing_value('Missing Markdown')
        return TutorialMarkdownDescriptor(raw.value or '')


class Plugin(lektor.pluginsystem.Plugin):

    name = 'Django Girls Taipei'
    description = 'Utilities to use in the Django Girls Taipei website.'

    def on_setup_env(self, **extra):
        self.env.types['tutorial-markdown'] = TutorialMarkdownType
