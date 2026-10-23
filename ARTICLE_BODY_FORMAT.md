# FintechRP article body format

How to write the HTML for an article's **Body** field so it picks up the site's
article styles (`static/css/article-body.css`). Paste the HTML into the admin
editor in **Source** mode (the "Source" button in the CKEditor toolbar). Pasting
into the normal view turns it into plain text and loses all formatting.

## Writing rules

- Keep visible article text free of hyphens, dashes and colons.
- Cite sources in the text as (Source, Year), matching the references list.
- Do not add inline styles, `<script>` tags or `<details>` tags. The site
  handles all styling, and the editor strips scripts.
- Every block below is optional except paragraphs and headings. Use each one
  at most once per article, apart from tooltips.

## Building blocks, in reading order

### Key numbers strip (top of the article, exactly three stats)

```html
<div class="fr-stats">
<div class="fr-stat"><strong>3.9%</strong><span>2026 world trade growth forecast</span></div>
<div class="fr-stat"><strong>47%</strong><span>Share of growth from AI goods</span></div>
<div class="fr-stat"><strong>14.8%</strong><span>AI goods share of world trade</span></div>
</div>
```

Keep each number short (up to about 6 characters) and each label under about 8 words.

### Headings and paragraphs

```html
<h2>A Number That Quietly Broke A Record</h2>
<p>First paragraph of the section.</p>
<p>Second paragraph of the section.</p>
```

Each heading is its own `<h2>`, never bold text inside a paragraph. Paragraphs
get a first-line indent and are justified on desktop automatically.

### Jargon tooltip (inside any paragraph)

```html
<abbr title="Plain English meaning in one sentence">Section 301 tariffs</abbr>
```

Use these for the 2 to 4 terms a general reader is most likely not to know.
Readers hover over the term on desktop or tap it on a phone.

### Pull quote (one per article)

```html
<blockquote class="fr-pullquote"><p>One striking sentence from the article.</p></blockquote>
```

### Chart (one per article)

A plain two-column table: label, then value. The site draws it as a bar chart,
and it still reads as a table if scripts are off.

```html
<table class="fr-chart">
<caption>AI goods share of world merchandise trade</caption>
<tbody>
<tr><td>2016 to 2023</td><td>7.5%</td></tr>
<tr><td>2026</td><td>14.8%</td></tr>
</tbody>
</table>
```

- Use 2 to 6 rows of comparable numbers in the same unit.
- The bar length comes from the number. The value text, such as "14.8%" or
  "$20B", is shown as written.

### Action box ("What You Can Actually Do About It")

```html
<div class="fr-action">
<h3>What You Can Actually Do About It</h3>
<p>Practical advice for the reader.</p>
</div>
```

### References (always last, shown collapsed)

```html
<div class="fr-references">
<p>WTO. (2026, October 8). Global trade outlook and statistics. <a href="https://www.wto.org/...">https://www.wto.org/...</a></p>
<p>Xinhua. (2026, October 9). WTO raises 2026 forecast. <a href="https://...">https://...</a></p>
</div>
```

Put one reference per `<p>`, with the link as a clickable `<a href>`.

## Key takeaways

The takeaways are **not** part of the Body either. Fill in the article's
**Key takeaways** field in the admin with 3 short sentences, one per line (4 at
most). They appear in a box above the body for readers who skim. Follow the same
writing rules as the body.

## Reader poll

The poll is **not** part of the Body. On the article's admin page, scroll to
**Reader poll** at the bottom, click "Add another", and fill in:

- **Question**: one question about the article.
- **Options**: 2 to 6 answers, one per line.

Each visitor gets one vote, and the results show as bars once they have voted.

## Older articles

Articles pasted in the old `<p><strong>Heading</strong><br />Text</p>` format
are upgraded on display automatically. The headings become real headings, and
a final "References" paragraph becomes the collapsible references block. They
do not need re-pasting.
