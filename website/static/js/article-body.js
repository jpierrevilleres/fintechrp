// Interactive pieces of the article body. Everything here enhances plain
// HTML that already reads fine without JavaScript.
(function () {
    const body = document.querySelector('.article-content');
    const articleEl = document.getElementById('article');
    const slug = articleEl ? articleEl.dataset.articleSlug : '';
    const articleUrl = articleEl ? articleEl.dataset.articleUrl : window.location.href;

    // Google Analytics event, tagged with the article. Respects the cookie
    // consent already configured in base.html; a no-op if GA isn't loaded.
    function track(name, params) {
        if (typeof window.gtag !== 'function') return;
        window.gtag('event', name, Object.assign({ article_slug: slug }, params || {}));
    }
    window.frTrack = track;

    function toast(message) {
        const el = document.createElement('div');
        el.className = 'alert alert-success position-fixed';
        el.style.cssText = 'right:20px;bottom:20px;z-index:2000';
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 2600);
    }

    function copyText(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text);
        }
        return Promise.reject(new Error('Clipboard unavailable'));
    }

    // Share buttons under each pull quote. X takes the quote as text;
    // LinkedIn only accepts a URL, so the quote is copied for pasting.
    function addQuoteShare(quote) {
        const text = quote.textContent.trim();
        if (!text) return;
        const bar = document.createElement('div');
        bar.className = 'fr-quote-share';

        function button(label, icon, method, onClick) {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'btn btn-outline-secondary';
            b.innerHTML = '<i class="bi ' + icon + ' me-1"></i>';
            b.appendChild(document.createTextNode(label));
            b.addEventListener('click', function () {
                onClick();
                track('quote_share', { method: method });
            });
            bar.appendChild(b);
        }

        button('Share on X', 'bi-twitter-x', 'x', function () {
            const url = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent('“' + text + '”')
                + '&url=' + encodeURIComponent(articleUrl);
            window.open(url, '_blank', 'noopener');
        });
        button('LinkedIn', 'bi-linkedin', 'linkedin', function () {
            copyText('“' + text + '”\n' + articleUrl).then(function () {
                toast('Quote copied, paste it into your LinkedIn post');
            }).catch(function () {});
            window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(articleUrl), '_blank', 'noopener');
        });
        button('Copy quote', 'bi-clipboard', 'copy', function () {
            copyText('“' + text + '”\n' + articleUrl).then(function () {
                toast('Quote copied');
            }).catch(function () {});
        });
        quote.appendChild(bar);
    }

    // Charts: <table class="fr-chart"> with a label column and a value column
    // becomes a horizontal bar chart. The original value text ("47%",
    // "$20B") is kept as the bar label; only the number is used for length.
    function buildChart(table) {
        const rows = [];
        table.querySelectorAll('tr').forEach(function (tr) {
            const cells = tr.querySelectorAll('th, td');
            if (cells.length < 2 || tr.parentElement.tagName === 'THEAD') return;
            const label = cells[0].textContent.trim();
            const text = cells[1].textContent.trim();
            const value = parseFloat(text.replace(/[^0-9.\-]/g, ''));
            if (!label || isNaN(value)) return;
            rows.push({ label: label, text: text, value: value });
        });
        if (rows.length === 0) return;

        const max = Math.max.apply(null, rows.map(function (r) { return r.value; }));
        const chart = document.createElement('figure');
        chart.className = 'fr-bars';
        chart.setAttribute('role', 'img');

        const caption = table.querySelector('caption');
        if (caption) {
            const title = document.createElement('figcaption');
            title.className = 'fr-bars-title';
            title.textContent = caption.textContent.trim();
            chart.appendChild(title);
        }
        chart.setAttribute('aria-label', rows.map(function (r) {
            return r.label + ' ' + r.text;
        }).join(', '));

        const fills = [];
        rows.forEach(function (r) {
            const row = document.createElement('div');
            row.className = 'fr-bar-row';
            const label = document.createElement('div');
            label.textContent = r.label;
            const track = document.createElement('div');
            track.className = 'fr-bar-track';
            const fill = document.createElement('div');
            fill.className = 'fr-bar-fill';
            fill.textContent = r.text;
            fill.dataset.width = max > 0 ? Math.max(0, r.value / max * 100) + '%' : '0%';
            track.appendChild(fill);
            row.appendChild(label);
            row.appendChild(track);
            chart.appendChild(row);
            fills.push(fill);
        });
        table.replaceWith(chart);

        // Grow the bars when the chart scrolls into view
        const grow = function () { fills.forEach(function (f) { f.style.width = f.dataset.width; }); };
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting) { grow(); observer.disconnect(); }
            }, { threshold: 0.3 });
            observer.observe(chart);
        } else {
            grow();
        }
    }

    if (body) {
        body.querySelectorAll('table.fr-chart').forEach(buildChart);
        body.querySelectorAll('.fr-pullquote').forEach(addQuoteShare);

        // Jargon tooltips: <abbr title="plain English meaning">term</abbr>.
        // tabindex lets phone users tap to show the meaning.
        if (window.bootstrap && bootstrap.Tooltip) {
            body.querySelectorAll('abbr[title]').forEach(function (el) {
                el.setAttribute('tabindex', '0');
                new bootstrap.Tooltip(el, { trigger: 'hover focus' });
                el.addEventListener('shown.bs.tooltip', function () {
                    track('tooltip_view', { term: el.textContent.trim() });
                }, { once: true });
            });
        }

        body.querySelectorAll('details.fr-references').forEach(function (d) {
            d.addEventListener('toggle', function () {
                if (d.open) track('references_open');
            });
        });

        // How far readers get through the article body (not the whole
        // page, so comments and the footer don't count as reading)
        const marks = [25, 50, 75, 100];
        const reached = {};
        let ticking = false;
        function checkDepth() {
            ticking = false;
            const rect = body.getBoundingClientRect();
            const read = (window.innerHeight - rect.top) / rect.height * 100;
            marks.forEach(function (m) {
                if (read >= m && !reached[m]) {
                    reached[m] = true;
                    track('article_scroll', { percent: m });
                }
            });
            if (reached[100]) window.removeEventListener('scroll', onScroll);
        }
        function onScroll() {
            if (!ticking) { ticking = true; requestAnimationFrame(checkDepth); }
        }
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    // Share menu under the title, and the "Keep reading" cards
    document.querySelectorAll('[data-share-method]').forEach(function (el) {
        el.addEventListener('click', function () {
            track('share', { method: el.dataset.shareMethod, content_type: 'article', item_id: slug });
        });
    });
    document.querySelectorAll('[data-related-slug]').forEach(function (el) {
        el.addEventListener('click', function () {
            track('related_article_click', { target_slug: el.dataset.relatedSlug });
        });
    });

    // Reader poll
    const poll = document.getElementById('poll');
    if (!poll) return;
    const form = poll.querySelector('form');
    if (!form) return;

    function renderResults(data) {
        const list = document.createElement('div');
        data.options.forEach(function (o) {
            const item = document.createElement('div');
            item.className = 'fr-poll-result' + (o.id === data.voted ? ' is-mine' : '');
            const label = document.createElement('div');
            label.className = 'fr-poll-result-label';
            const text = document.createElement('span');
            text.textContent = o.text;
            const pct = document.createElement('span');
            pct.textContent = o.percent + '%';
            label.appendChild(text);
            label.appendChild(pct);
            const bar = document.createElement('div');
            bar.className = 'progress';
            const fill = document.createElement('div');
            fill.className = 'progress-bar';
            fill.style.width = o.percent + '%';
            bar.appendChild(fill);
            item.appendChild(label);
            item.appendChild(bar);
            list.appendChild(item);
        });
        const total = document.createElement('div');
        total.className = 'fr-poll-total';
        total.textContent = data.total + (data.total === 1 ? ' vote' : ' votes') + ' · thanks for voting';
        list.appendChild(total);
        form.replaceWith(list);
    }

    form.addEventListener('submit', function (e) {
        const option = e.submitter && e.submitter.value;
        if (!option) return;  // let the browser submit normally
        e.preventDefault();
        form.querySelectorAll('button').forEach(function (b) { b.disabled = true; });
        const data = new FormData(form);
        data.append('option', option);
        fetch(form.action, {
            method: 'POST',
            body: data,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        }).then(function (r) {
            if (!r.ok) throw new Error('Vote failed');
            return r.json();
        }).then(function (data) {
            track('poll_vote', { poll_option: e.submitter.textContent.trim() });
            renderResults(data);
        }).catch(function () {
            form.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
        });
    });
})();
