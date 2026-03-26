/* ═══════════════════════════════════════════════════════════════
   PYTHAGOREAN COSMOS — Core JavaScript
   Navigation, search, filtering, animations, data
   ═══════════════════════════════════════════════════════════════ */

// ── Navigation ──
document.addEventListener('DOMContentLoaded', () => {
  // Scroll behavior for nav
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 50);
    });
  }

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-mobile-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
    });
  }

  // Active nav link
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href && (href.endsWith(currentPage) || (currentPage === 'index.html' && href === './' ))) {
      a.classList.add('active');
    }
  });

  // Scroll animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.animate-in').forEach(el => observer.observe(el));

  // Animated counters
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    const duration = 2000;
    const start = performance.now();

    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(el, target, duration);
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    counterObserver.observe(el);
  });
});

function animateCounter(el, target, duration) {
  const start = performance.now();
  const format = el.dataset.format;

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    const current = Math.floor(eased * target);

    if (format === 'comma') {
      el.textContent = current.toLocaleString();
    } else {
      el.textContent = current;
    }

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      if (format === 'comma') {
        el.textContent = target.toLocaleString();
      } else {
        el.textContent = target;
      }
      if (el.dataset.suffix) {
        el.textContent += el.dataset.suffix;
      }
    }
  }

  requestAnimationFrame(update);
}

// ── Shared Navigation HTML ──
function getNavHTML(activePage) {
  const pages = [
    { href: './index.html', label: 'Home', id: 'index.html' },
    { href: './pages/theorems.html', label: 'Theorems', id: 'theorems.html' },
    { href: './pages/library.html', label: 'Library', id: 'library.html' },
    { href: './pages/deep-dives/berggren-tree.html', label: 'Deep Dives', id: 'deep-dives' },
    { href: './pages/codebase.html', label: 'Codebase', id: 'codebase.html' },
    { href: './pages/about.html', label: 'About', id: 'about.html' },
  ];

  // Fix relative paths based on page depth
  const depth = activePage.includes('deep-dives') ? 2 : (activePage === 'index.html' ? 0 : 1);

  return pages.map(p => {
    let href = p.href;
    if (depth === 1) href = href.replace('./', '../');
    if (depth === 2) href = href.replace('./', '../../');
    const isActive = activePage === p.id || (p.id === 'deep-dives' && activePage.includes('deep-dives'));
    return `<li><a href="${href}" class="${isActive ? 'active' : ''}">${p.label}</a></li>`;
  }).join('');
}

// ── Papers Data ──
const PAPER_CATEGORIES = {
  'Research Paper': { color: 'indigo', icon: '📄' },
  'Scientific American': { color: 'cyan', icon: '🔬' },
  'Lab Notebook': { color: 'emerald', icon: '🔬' },
  'Vision & Foundations': { color: 'violet', icon: '🎯' },
  'Catalog & Report': { color: 'amber', icon: '📊' },
  'Code & Experiments': { color: 'rose', icon: '💻' },
  'Team Notes': { color: 'blue', icon: '👥' },
  'Other': { color: 'emerald', icon: '📎' }
};

function categorizePaper(filename) {
  const lower = filename.toLowerCase();
  if (lower.includes('sciam') || lower.includes('scientific_american') || lower.includes('scientificamerican'))
    return 'Scientific American';
  if (lower.includes('lab_notebook') || lower.includes('labnotebook'))
    return 'Lab Notebook';
  if (lower.includes('team') || lower.includes('teamnotes') || lower.includes('teamresearch'))
    return 'Team Notes';
  if (lower.includes('catalog') || lower.includes('report') || lower.includes('cleanup') || lower.includes('directions'))
    return 'Catalog & Report';
  if (lower.endsWith('.py') || lower.endsWith('.py.txt') || lower.includes('experiment'))
    return 'Code & Experiments';
  if (lower.startsWith('0') || lower.includes('vision') || lower.includes('overview'))
    return 'Vision & Foundations';
  if (lower.includes('research') || lower.includes('paper') || lower.includes('frontier') ||
      lower.includes('moonshot') || lower.includes('comprehensive'))
    return 'Research Paper';
  if (lower.endsWith('.md')) return 'Research Paper';
  return 'Other';
}

function formatPaperTitle(filename) {
  return filename
    .replace(/\.md$/, '')
    .replace(/\.py\.txt$/, '.py')
    .replace(/\.py$/, ' (Python)')
    .replace(/\.tex$/, ' (LaTeX)')
    .replace(/\.pdf$/, ' (PDF)')
    .replace(/_/g, ' ')
    .replace(/ \(\d+\)/, '')
    .replace(/([a-z])([A-Z])/g, '$1 $2');
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Theorem Domain Data ──
const THEOREM_DOMAINS = [
  { id: 'pythagorean', name: 'Pythagorean Triples & Berggren Tree', count: 350, icon: '🌲' },
  { id: 'channels', name: 'Four-Channel Signatures', count: 100, icon: '📡' },
  { id: 'compression', name: 'Compression Theory', count: 120, icon: '🗜️' },
  { id: 'quantum', name: 'Quantum Computing & Gates', count: 500, icon: '⚛️' },
  { id: 'stereographic', name: 'Stereographic & Decoder', count: 300, icon: '🔮' },
  { id: 'flt4', name: 'FLT4 & Congruent Numbers', count: 30, icon: '🔢' },
  { id: 'lorentz', name: 'Lorentz & Light Cone', count: 250, icon: '💡' },
  { id: 'algebra', name: 'Algebraic Structures', count: 120, icon: '🔷' },
  { id: 'sl2', name: 'SL(2,ℤ) & Modular', count: 70, icon: '🌀' },
  { id: 'numbertheory', name: 'Number Theory', count: 250, icon: '🔣' },
  { id: 'combinatorics', name: 'Combinatorics & Graphs', count: 80, icon: '🕸️' },
  { id: 'topology', name: 'Topology & Dynamics', count: 100, icon: '🍩' },
  { id: 'category', name: 'Category & Representation', count: 60, icon: '🏗️' },
  { id: 'mobius', name: 'Möbius & Order Classification', count: 80, icon: '♾️' },
  { id: 'crystallizer', name: 'Crystallizer & Neural Arch', count: 250, icon: '💎' },
  { id: 'applied', name: 'Applied Mathematics', count: 250, icon: '⚙️' },
  { id: 'advanced', name: 'Advanced Topics', count: 348, icon: '🚀' },
];

// ── Markdown Renderer (full-featured) ──
function renderMarkdown(text) {
  if (!text) return '';

  // Normalize line endings
  text = text.replace(/\r\n/g, '\n');

  // Extract fenced code blocks to protect from further processing
  const codeBlocks = [];
  text = text.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    codeBlocks.push({ lang, code: code.replace(/</g, '&lt;').replace(/>/g, '&gt;') });
    return `%%CODEBLOCK_${codeBlocks.length - 1}%%`;
  });

  // Split into lines for block-level processing
  const lines = text.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Blank line
    if (line.trim() === '') { i++; continue; }

    // Headers
    const hMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (hMatch) {
      const lvl = hMatch[1].length;
      blocks.push(`<h${lvl}>${inlineFormat(hMatch[2])}</h${lvl}>`);
      i++; continue;
    }

    // Horizontal rule
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(line.trim())) {
      blocks.push('<hr>');
      i++; continue;
    }

    // Blockquote
    if (line.startsWith('>')) {
      let bqLines = [];
      while (i < lines.length && (lines[i].startsWith('>') || (lines[i].trim() !== '' && bqLines.length > 0 && !lines[i].match(/^#{1,6}\s/)))) {
        bqLines.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      blocks.push(`<blockquote>${renderMarkdown(bqLines.join('\n'))}</blockquote>`);
      continue;
    }

    // Unordered list
    if (/^\s*[-*+]\s/.test(line)) {
      let listItems = [];
      while (i < lines.length && /^\s*[-*+]\s/.test(lines[i])) {
        listItems.push(lines[i].replace(/^\s*[-*+]\s+/, ''));
        i++;
      }
      blocks.push('<ul>' + listItems.map(li => `<li>${inlineFormat(li)}</li>`).join('') + '</ul>');
      continue;
    }

    // Ordered list
    if (/^\s*\d+[.)]\s/.test(line)) {
      let listItems = [];
      while (i < lines.length && /^\s*\d+[.)]\s/.test(lines[i])) {
        listItems.push(lines[i].replace(/^\s*\d+[.)]\s+/, ''));
        i++;
      }
      blocks.push('<ol>' + listItems.map(li => `<li>${inlineFormat(li)}</li>`).join('') + '</ol>');
      continue;
    }

    // Table
    if (line.includes('|') && line.trim().startsWith('|')) {
      let tableLines = [];
      while (i < lines.length && lines[i].includes('|') && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      if (tableLines.length >= 2) {
        let thead = '', tbody = '';
        const headerCells = tableLines[0].split('|').filter(c => c.trim() !== '').map(c => c.trim());
        thead = '<thead><tr>' + headerCells.map(c => `<th>${inlineFormat(c)}</th>`).join('') + '</tr></thead>';
        const bodyStart = (tableLines[1] && /^[\s|:-]+$/.test(tableLines[1])) ? 2 : 1;
        const bodyRows = tableLines.slice(bodyStart).map(row => {
          const cells = row.split('|').filter(c => c.trim() !== '').map(c => c.trim());
          return '<tr>' + cells.map(c => `<td>${inlineFormat(c)}</td>`).join('') + '</tr>';
        }).join('');
        tbody = `<tbody>${bodyRows}</tbody>`;
        blocks.push(`<div class="table-wrapper"><table class="reader-table">${thead}${tbody}</table></div>`);
        continue;
      }
    }

    // Code block placeholder
    if (line.startsWith('%%CODEBLOCK_')) {
      blocks.push(line);
      i++; continue;
    }

    // Paragraph: collect consecutive non-empty, non-special lines
    let paraLines = [];
    while (i < lines.length && lines[i].trim() !== '' && !lines[i].match(/^#{1,6}\s/) && !lines[i].match(/^(-{3,}|\*{3,}|_{3,})$/) && !lines[i].startsWith('>') && !/^\s*[-*+]\s/.test(lines[i]) && !/^\s*\d+[.)]\s/.test(lines[i]) && !lines[i].startsWith('%%CODEBLOCK_') && !(lines[i].includes('|') && lines[i].trim().startsWith('|'))) {
      paraLines.push(lines[i]);
      i++;
    }
    if (paraLines.length > 0) {
      blocks.push(`<p>${inlineFormat(paraLines.join('\n'))}</p>`);
    }
  }

  let html = blocks.join('\n');

  // Restore code blocks
  html = html.replace(/%%CODEBLOCK_(\d+)%%/g, (_, idx) => {
    const cb = codeBlocks[parseInt(idx)];
    return `<div class="reader-code"><div class="reader-code-header">${cb.lang || 'text'}</div><pre><code>${cb.code}</code></pre></div>`;
  });

  return html;
}

function inlineFormat(text) {
  return text
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/~~(.+?)~~/g, '<del>$1</del>')
    .replace(/\n/g, '<br>');
}
