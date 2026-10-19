(function () {
    'use strict';

    const slideEl = document.getElementById('slide');
    const emptyEl = document.getElementById('empty-state');
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');
    const firstBtn = document.getElementById('first');
    const lastBtn = document.getElementById('last');
    const counterEl = document.getElementById('counter');
    const progressBar = document.getElementById('progress-bar');
    const fullscreenBtn = document.getElementById('fullscreen');
    const tocBtn = document.getElementById('toc-btn');
    const tocEl = document.getElementById('toc');
    const tocCloseBtn = document.getElementById('toc-close');
    const tocList = document.getElementById('toc-list');
    const mascotEl = document.getElementById('mascot');

    const MASCOT_BASE = '../../img/mascot/';

    let slides = [];
    let current = 0;

    function getParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    }

    function normalizeSrc(src) {
        // Never point to .md files directly — MkDocs serves rendered HTML at
        // directory-style URLs. Strip trailing `.md` and `/index.md`.
        let s = src.trim();
        if (s.endsWith('/index.md')) s = s.slice(0, -'index.md'.length);
        else if (s.endsWith('.md')) s = s.slice(0, -'.md'.length) + '/';
        if (!s.endsWith('/') && !s.endsWith('.html')) s += '/';
        return s;
    }

    function extractArticle(htmlText) {
        const doc = new DOMParser().parseFromString(htmlText, 'text/html');
        return doc.querySelector('article.md-content__inner')
            || doc.querySelector('article')
            || doc.querySelector('main')
            || doc.body;
    }

    function splitByHr(root) {
        const chunks = [];
        let current = document.createElement('div');
        current.className = 'slide-inner';
        for (const node of Array.from(root.childNodes)) {
            if (node.nodeType === 1 && node.tagName === 'HR') {
                if (current.childNodes.length) chunks.push(current);
                current = document.createElement('div');
                current.className = 'slide-inner';
            } else {
                current.appendChild(node.cloneNode(true));
            }
        }
        if (current.childNodes.length) chunks.push(current);
        return chunks.filter(c => c.textContent.trim().length > 0);
    }

    function removeEditAndPermalinks(el) {
        el.querySelectorAll('.headerlink, .md-content__button, .md-source-file').forEach(n => n.remove());
    }

    function firstHeadingText(el) {
        const h = el.querySelector('h1, h2, h3');
        if (h) return h.textContent.replace(/¶$/, '').trim();
        const p = el.querySelector('p');
        return p ? p.textContent.slice(0, 60).trim() : 'Slide';
    }

    function render() {
        if (!slides.length) return;
        slideEl.innerHTML = '';
        slideEl.appendChild(slides[current].cloneNode(true));
        slideEl.classList.toggle('title-slide', current === 0);
        const isLast = current === slides.length - 1;
        mascotEl.hidden = false;
        mascotEl.src = MASCOT_BASE + (isLast ? 'celebration.png' : 'neutral.png');
        mascotEl.alt = isLast ? 'Bloom celebrating' : 'Bloom the elephant mascot';
        mascotEl.classList.toggle('celebration', isLast);
        counterEl.textContent = `${current + 1} / ${slides.length}`;
        progressBar.style.width = `${((current + 1) / slides.length) * 100}%`;
        prevBtn.disabled = current === 0;
        firstBtn.disabled = current === 0;
        nextBtn.disabled = current === slides.length - 1;
        lastBtn.disabled = current === slides.length - 1;
        updateTocActive();
    }

    function go(delta) {
        const next = Math.min(Math.max(current + delta, 0), slides.length - 1);
        if (next !== current) {
            current = next;
            render();
        }
    }

    function goTo(index) {
        if (index >= 0 && index < slides.length) {
            current = index;
            render();
        }
    }

    function buildToc() {
        tocList.innerHTML = '';
        slides.forEach((chunk, i) => {
            const li = document.createElement('li');
            li.textContent = firstHeadingText(chunk);
            li.addEventListener('click', () => {
                goTo(i);
                tocEl.hidden = true;
            });
            tocList.appendChild(li);
        });
    }

    function updateTocActive() {
        tocList.querySelectorAll('li').forEach((li, i) => li.classList.toggle('active', i === current));
    }

    async function load(rawSrc) {
        const src = normalizeSrc(rawSrc);
        try {
            const res = await fetch(src);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const text = await res.text();
            const article = extractArticle(text);
            removeEditAndPermalinks(article);
            slides = splitByHr(article);
            if (!slides.length) throw new Error('No slides found. Use "---" on its own line to separate slides.');
            emptyEl.hidden = true;
            slideEl.hidden = false;
            buildToc();
            const startParam = parseInt(getParam('slide') || '1', 10);
            current = Math.min(Math.max(startParam - 1, 0), slides.length - 1);
            render();
        } catch (err) {
            showError(`Could not load slides from "${src}": ${err.message}`);
        }
    }

    function showError(msg) {
        emptyEl.hidden = false;
        slideEl.hidden = true;
        emptyEl.innerHTML = `<h1>Slide Viewer</h1><p style="color:#c0392b">${msg}</p>`;
    }

    function showEmpty() {
        emptyEl.hidden = false;
        slideEl.hidden = true;
        mascotEl.hidden = true;
        counterEl.textContent = '0 / 0';
        progressBar.style.width = '0%';
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        firstBtn.disabled = true;
        lastBtn.disabled = true;
    }

    prevBtn.addEventListener('click', () => go(-1));
    nextBtn.addEventListener('click', () => go(1));
    firstBtn.addEventListener('click', () => goTo(0));
    lastBtn.addEventListener('click', () => goTo(slides.length - 1));

    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) document.documentElement.requestFullscreen();
        else document.exitFullscreen();
    });

    tocBtn.addEventListener('click', () => { tocEl.hidden = !tocEl.hidden; });
    tocCloseBtn.addEventListener('click', () => { tocEl.hidden = true; });

    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        switch (e.key) {
            case 'ArrowRight':
            case 'PageDown':
            case ' ':
                e.preventDefault(); go(1); break;
            case 'ArrowLeft':
            case 'PageUp':
                e.preventDefault(); go(-1); break;
            case 'Home':
                e.preventDefault(); goTo(0); break;
            case 'End':
                e.preventDefault(); goTo(slides.length - 1); break;
            case 'f': case 'F': fullscreenBtn.click(); break;
            case 't': case 'T': tocBtn.click(); break;
            case 'Escape': tocEl.hidden = true; break;
        }
    });

    const src = getParam('src');
    if (src) load(src);
    else showEmpty();
})();
