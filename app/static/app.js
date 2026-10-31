'use strict';
const ui = window.tabler;
const $ = (selector) => document.querySelector(selector);
const all = (selector) => [...document.querySelectorAll(selector)];
const toast = (message) => { $('#toast-message').textContent = message; ui.Toast.getOrCreateInstance($('#demo-toast'), {delay: 3500}).show(); };
all('[data-bs-toggle="tooltip"]').forEach(el => ui.Tooltip.getOrCreateInstance(el));
all('[data-bs-toggle="popover"]').forEach(el => ui.Popover.getOrCreateInstance(el));
all('.demo-toast').forEach(el => el.addEventListener('click', () => toast(`Кнопка «${el.textContent.trim() || el.getAttribute('aria-label')}» работает.`)));
$('#toast-button').addEventListener('click', () => toast('Это всплывающее уведомление Tabler. Всё работает локально.'));
all('.color-swatch').forEach(el => el.addEventListener('click', () => { $('#color-result').textContent = `Цвет: ${el.dataset.color} · класс bg-${el.dataset.color}`; }));
all('.icon-preview').forEach(el => el.addEventListener('click', () => { $('#icon-result').textContent = `SVG-иконка: ${el.dataset.iconName}`; }));
const closeMenu = () => { document.body.classList.remove('menu-open'); $('#menu-toggle').setAttribute('aria-expanded','false'); };
$('#menu-toggle').addEventListener('click', () => { const open = document.body.classList.toggle('menu-open'); $('#menu-toggle').setAttribute('aria-expanded', String(open)); });
$('#sidebar-shade').addEventListener('click', closeMenu);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
all('.side-nav a').forEach(el => el.addEventListener('click', closeMenu));
const sections = all('main section[id], .section-heading[id]');
const observer = new IntersectionObserver(entries => { const entry = entries.filter(e => e.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0]; if (!entry) return; all('.side-nav a').forEach(a => { a.classList.toggle('active',a.hash === '#'+entry.target.id); }); }, {rootMargin:'-70px 0px -65% 0px',threshold:0});
sections.forEach(s => observer.observe(s));
const isDark = () => document.documentElement.dataset.bsTheme === 'dark';
let lineChart, donutChart;
function setTheme(theme) {
  document.documentElement.dataset.bsTheme = theme;
  $('#theme-select').value = theme;
  $('#theme-toggle').setAttribute('aria-label', theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему');
  try { localStorage.setItem('tabler-theme', theme); } catch {}
  if (lineChart) { lineChart.options.scales.y.grid.color = isDark() ? '#303649' : '#eef0f5'; lineChart.update(); }
}
$('#theme-select').value = isDark() ? 'dark' : 'light';
$('#theme-toggle').addEventListener('click', () => setTheme(isDark() ? 'light' : 'dark'));
$('#theme-select').addEventListener('change', e => setTheme(e.target.value));
try { $('#compact-switch').checked = localStorage.getItem('tabler-compact') === 'true'; } catch {}
document.body.classList.toggle('compact-table', $('#compact-switch').checked);
$('#compact-switch').addEventListener('change', e => { document.body.classList.toggle('compact-table', e.target.checked); try { localStorage.setItem('tabler-compact', e.target.checked); } catch {} });
const chartSets = {
  week:{labels:['Пн','Вт','Ср','Чт','Пт','Сб','Вс'],views:[2800,3700,3100,4600,3900,5200,4380],people:[1200,1900,1500,2600,2100,3000,2460]},
  month:{labels:['01','03','05','07','09','11','13','15','17','19','21','23','25','27','29','31'],views:[2100,2600,2200,3400,3000,3800,3200,4400,3900,4600,4200,5100,4500,5300,4800,5800],people:[800,1100,900,1600,1200,1700,1400,2100,1800,2300,2000,2700,2200,2900,2600,3200]}
};
Chart.defaults.font.family = 'system-ui, sans-serif'; Chart.defaults.font.size = 10; Chart.defaults.color = '#989fb0';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
lineChart = new Chart($('#activity-chart'), {type:'line',data:{labels:chartSets.week.labels,datasets:[{label:'Просмотры',data:chartSets.week.views,borderColor:'#8560da',backgroundColor:'rgba(133,96,218,.09)',fill:true,borderWidth:2.5,tension:.35,pointRadius:0,pointHoverRadius:4},{label:'Посетители',data:chartSets.week.people,borderColor:'#62a4ee',backgroundColor:'rgba(98,164,238,.04)',fill:true,borderWidth:2,tension:.35,pointRadius:0,pointHoverRadius:4}]},options:{responsive:true,maintainAspectRatio:false,animation:reducedMotion?false:undefined,interaction:{intersect:false,mode:'index'},plugins:{legend:{display:false}},scales:{x:{grid:{display:false},border:{display:false}},y:{beginAtZero:true,ticks:{stepSize:2000,callback:value=>value>=1000?value/1000+'k':value},grid:{color:isDark()?'#303649':'#eef0f5'},border:{display:false}}}}});
donutChart = new Chart($('#donut-chart'),{type:'doughnut',data:{labels:['Прямые','Поиск','Переходы','Другие'],datasets:[{data:[42,32,18,8],backgroundColor:['#8560da','#62a4ee','#4eb9a6','#dce0e9'],borderWidth:0,spacing:4,borderRadius:4}]},options:{responsive:true,maintainAspectRatio:false,cutout:'82%',animation:reducedMotion?false:undefined,plugins:{legend:{display:false}}}});
all('.chart-period').forEach(btn => btn.addEventListener('click', () => { all('.chart-period').forEach(b => { b.classList.toggle('active',b===btn); b.setAttribute('aria-pressed',String(b===btn)); }); const d = chartSets[btn.dataset.period]; lineChart.data.labels=d.labels; lineChart.data.datasets[0].data=d.views; lineChart.data.datasets[1].data=d.people; lineChart.update(); }));
new TomSelect('#project-tags',{plugins:['remove_button'],maxItems:4,create:false});
new Litepicker({element:$('#date-picker'),singleMode:true,format:'DD.MM.YYYY',lang:'ru-RU',dropdowns:{minYear:2020,maxYear:2035,months:true,years:true}});
$('#demo-range').addEventListener('input', e => { $('#range-value').value = e.target.value+'%'; });
$('#demo-switch').addEventListener('change', e => { $('#switch-state').textContent = e.target.checked ? '· включены' : '· выключены'; });
[['#demo-file','#file-name'],['#empty-file','#empty-file-result']].forEach(([input,result]) => { $(input).addEventListener('change',e => { $(result).textContent = e.target.files[0] ? `Выбран: ${e.target.files[0].name} · ${Math.ceil(e.target.files[0].size/1024)} КБ (локально)` : 'Файл не выбран'; }); });
all('.demo-pill').forEach(el => el.addEventListener('click', () => { all('.demo-pill').forEach(p => {p.classList.toggle('active',p===el);p.setAttribute('aria-pressed',String(p===el));}); $('#nav-result').textContent='Выбрано: '+el.textContent; }));
all('.step-item').forEach((el,index) => el.addEventListener('click', () => {all('.step-item').forEach((step,i) => step.classList.toggle('active',i<=index));toast('Текущий этап: '+el.textContent);}));
function updateTasks() { const boxes=all('.task-checkbox'); $('#task-count').textContent=`Выполнено ${boxes.filter(b=>b.checked).length} из ${boxes.length}`; }
all('.task-checkbox').forEach((el,i) => {try {const stored=localStorage.getItem('tabler-task-'+i);if(stored!==null)el.checked=stored==='true';} catch {} el.addEventListener('change',() => {try {localStorage.setItem('tabler-task-'+i,el.checked);} catch {} updateTasks();});}); updateTasks();
$('#loading-demo').addEventListener('click', async e => {const btn=e.currentTarget;btn.disabled=true;btn.textContent='Загрузка…';await new Promise(r=>setTimeout(r,1200));btn.disabled=false;btn.textContent='Запустить';toast('Загрузка завершена. Это локальная демонстрация.');});
document.body.addEventListener('projectCreated', () => toast('Проект сохранён. Таблица обновлена.'));
document.body.addEventListener('htmx:responseError', () => toast('Сервер не смог выполнить запрос. Повторите попытку.'));
document.body.addEventListener('htmx:sendError', () => toast('Нет связи с локальным сервером. Проверьте, запущено ли приложение.'));
