from __future__ import unicode_literals

import collections
import re

import mistune
import slugify

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_by_name


class BlockGrammar(mistune.BlockGrammar):

    # Fix trailing newline bug in Mistune.
    block_code = re.compile(r'^( {4}[^\n]+\n)+')

    os_switch = re.compile(
        r'^ *\({3} *([\w _-]+) *\n'     # ((( class names
        r'([\s\S]+?)\s*'
        r'\){3} *(?:\n+|$)'             # )))
    )


class BlockLexer(mistune.BlockLexer):

    grammar_class = BlockGrammar
    default_rules = mistune.BlockLexer.default_rules[:]
    default_rules.insert(5, 'os_switch')

    def parse_os_switch(self, m):
        self.tokens.append({
            'type': 'os_switch_open',
            'os': m.group(1),
        })
        self.parse(m.group(2))
        self.tokens.append({
            'type': 'os_switch_close',
        })


class InlineGrammar(mistune.InlineGrammar):

    # Math inline. Two dollars (not one). We don't implement block math yet.
    math = re.compile(r'^(\$+)\s*(.*?[^`])\s*\1(?!\$)')

    # Override plain text pattern to add the dollar sign as a markup char.
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~\$]|https?://| {2,}\n|$)')


class InlineLexer(mistune.InlineLexer):

    grammar_class = InlineGrammar
    default_rules = mistune.InlineLexer.default_rules[:]
    default_rules.insert(8, 'math')

    def output_math(self, m):
        text = m.group(2)
        return self.renderer.inline_math(text)


class Markdown(mistune.Markdown):

    def __init__(self, renderer=None, inline=None, block=None, **kwargs):
        if block is None:
            block = BlockLexer
        if inline is None:
            inline = InlineLexer
        super(Markdown, self).__init__(renderer, inline, block, **kwargs)

    def output_os_switch_open(self):
        return self.renderer.os_switch_open(os=self.token['os'])

    def output_os_switch_close(self):
        return self.renderer.os_switch_close()


class Renderer(mistune.Renderer):
    """Custom Markdown to HTML renderer.
    """
    def __init__(self, formatter, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.formatter = formatter
        self.id_slugs = collections.defaultdict(int)

    def os_switch_open(self, os):
        return '<div class="os {name}">\n'.format(name=os)

    def os_switch_close(self):
        return '</div>\n'

    def header(self, text, level, raw=None):
        """Auto header ID from slug of text.
        """
        slug = slugify.slugify(text)
        if self.id_slugs[slug]:
            slug = '{slug}-{n}'.format(slug=slug, n=self.id_slugs[slug])
        self.id_slugs[slug] += 1
        return '<h{level} id="{id}">{text}</h{level}>\n'.format(
            level=level, text=text, id=slug,
        )

    def block_code(self, code, lang):
        """Implement syntax highlighting with Pygments.
        """
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            return super(Renderer, self).block_code(code, lang)
        return highlight(code, lexer, self.formatter)

    def inline_math(self, src):
        return '<span class="math">{src}</span>'.format(src=src)


class TutorialRenderer(Renderer):
    """Custom Markdown to HTML renderer for tutorial pages.
    """
    CONSOLE_DELIMITER_PATTERN = re.compile(r'^---([\w-]+)$', re.MULTILINE)

    def block_code(self, code, lang):
        """Implement console language rendering.
        """
        if lang == 'console':
            return self.block_console(code)
        return super(TutorialRenderer, self).block_code(code, lang)

    def block_console(self, content, default='default'):
        """Special OS-specific "console language"
        A console block is similar to a code block, but instead of outputting
        content verbatim, a console block can optionally use ``---(os-name)``
        delimiters to denote OS-specific commands. The first block is the
        fallback block, and its OS is specified in ``default``.
        """
        pattern = self.CONSOLE_DELIMITER_PATTERN
        matches = [b.strip() for b in pattern.split(content)]
        matches.insert(0, default)

        it = iter(matches)
        str_format = '<pre class="os {name}"><code>{code}</code></pre>'
        return '<div>{code}</div>\n'.format(code='\n'.join([
            str_format.format(name=name, code=next(it)) for name in it
        ]))

    def table(self, header, body):
        """Render table with Bootstrap .table class
        """
        str_format = (
            '<table class="table">\n<thead>{thead}</thead>\n'
            '<tbody>\n{tbody}</tbody>\n</table>\n'
        )
        return str_format.format(thead=header, tbody=body)


def markdown_to_html(markdown, style=None, renderer_cls=Renderer):
    """Renders given Markdown input to HTML.
    """
    if style is None:
        style = 'default'
    try:
        formatter = HtmlFormatter(style=style)
    except ClassNotFound:
        formatter = HtmlFormatter(style='default')
    renderer = renderer_cls(formatter=formatter)
    md = Markdown(renderer=renderer)
    html = md.render(markdown)
    return html, formatter.get_style_defs('.highlight > pre')
