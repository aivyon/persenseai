(() => {
  const toggle=document.querySelector('.nav-toggle'), nav=document.querySelector('#nav');
  toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));nav.classList.toggle('open',!open)});
  document.querySelectorAll('#nav a').forEach(link=>link.addEventListener('click',()=>{nav.classList.remove('open');toggle?.setAttribute('aria-expanded','false')}));
  const grid=document.querySelector('#project-grid'); if(!grid)return;
  fetch('data/projects.json').then(r=>{if(!r.ok)throw new Error('Project data unavailable');return r.json()}).then(projects=>{
    grid.innerHTML=projects.map(p=>`<article class="project-card"><img src="${p.image}" alt="Synthetic ${p.title} dashboard preview" width="1440" height="1111" loading="lazy"><div class="project-card-body"><div class="tag-row"><span>${p.status}</span><span>${p.badge}</span></div><h3>${p.title}</h3><p class="question">${p.question}</p><p>${p.description}</p><p class="limit"><strong>Limit:</strong> ${p.limitations}</p><a href="${p.page}">View public project page →</a></div></article>`).join('');
  }).catch(()=>{grid.innerHTML='<p>Project cards are temporarily unavailable. Project pages remain listed in the sitemap.</p>'});
})();
