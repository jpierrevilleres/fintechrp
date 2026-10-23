"""Reader poll defined inside an article body.

An article body can end with:

    <div class="fr-poll">
    <p>Poll question?</p>
    <ul>
    <li>First option</li>
    <li>Second option</li>
    </ul>
    </div>

Saving the article in the admin creates or updates its Poll from this block
(see ArticleAdmin.save_related), and the block itself is removed when the body
is displayed, since the template renders the interactive poll instead.
"""
import html
import re

POLL_BLOCK_RE = re.compile(r'<div class="fr-poll">(.*?)</div>', re.IGNORECASE | re.DOTALL)
_QUESTION_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL)
_OPTION_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r'<[^>]+>')

MIN_OPTIONS, MAX_OPTIONS = 2, 6


class PollBlockError(ValueError):
    pass


def _text(fragment):
    text = html.unescape(_TAG_RE.sub('', fragment))
    return ' '.join(text.split())


def parse_poll_block(body):
    """Return (question, options) from the body's poll block, or None when
    there is no block. Raises PollBlockError if the block is malformed."""
    match = POLL_BLOCK_RE.search(body or '')
    if not match:
        return None
    inner = match.group(1)

    question_match = _QUESTION_RE.search(inner)
    question = _text(question_match.group(1)) if question_match else ''
    if not question:
        raise PollBlockError('the poll block has no question (a <p> before the options).')
    if len(question) > 255:
        raise PollBlockError('the poll question is longer than 255 characters.')

    options = list(dict.fromkeys(
        text for text in (_text(o) for o in _OPTION_RE.findall(inner)) if text
    ))
    if not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
        raise PollBlockError(
            f'the poll needs {MIN_OPTIONS} to {MAX_OPTIONS} options (<li> items), found {len(options)}.'
        )
    if any(len(o) > 200 for o in options):
        raise PollBlockError('each poll option must be 200 characters or fewer.')
    return question, options


def strip_poll_block(body):
    return POLL_BLOCK_RE.sub('', body or '')
