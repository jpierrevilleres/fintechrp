// Interactive pieces of the article body. Everything here enhances plain
// HTML that already reads fine without JavaScript.
(function () {
    const body = document.querySelector('.article-content');

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

        // Jargon tooltips: <abbr title="plain English meaning">term</abbr>.
        // tabindex lets phone users tap to show the meaning.
        if (window.bootstrap && bootstrap.Tooltip) {
            body.querySelectorAll('abbr[title]').forEach(function (el) {
                el.setAttribute('tabindex', '0');
                new bootstrap.Tooltip(el, { trigger: 'hover focus' });
            });
        }
    }

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
        }).then(renderResults).catch(function () {
            form.querySelectorAll('button').forEach(function (b) { b.disabled = false; });
        });
    });
})();
