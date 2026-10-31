try { document.documentElement.dataset.bsTheme = localStorage.getItem('tabler-theme') || 'light'; } catch { document.documentElement.dataset.bsTheme = 'light'; }
