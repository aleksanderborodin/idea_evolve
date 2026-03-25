// ======================================================================
// Alpha Evolve Dashboard — Client Logic
// ======================================================================

const PHASE_ORDER = ['not_started', 'planned', 'agents_running', 'agents_done', 'evaluator_done', 'critic_done', 'consistency_done', 'complete'];

let overviewData = null;
let solutionsData = null;
let knowledgeData = null;
let reportsData = null;
let filesData = null;

let solSort = { key: 'score', dir: -1 };
let solFilterGen = 'all';
let solFilterAgent = 'all';
let ideaFilterLc = 'all';

let activeAgentsData = null;
let agentRefreshTimer = null;
let refreshTimer = null;

// ----- Tab Navigation -----
document.querySelectorAll('.nav-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.dataset.tab;
    document.getElementById('tab-' + tab).classList.add('active');

    // Load data for tab if needed
    if (tab === 'overview') loadOverview();
    if (tab === 'solutions') loadSolutions();
    if (tab === 'knowledge') loadKnowledge();
    if (tab === 'reports') loadReports();
    if (tab === 'architecture') loadFiles();

    // Auto-refresh only on overview; agent refresh on pipeline
    clearInterval(refreshTimer);
    clearInterval(agentRefreshTimer);
    if (tab === 'overview') {
      refreshTimer = setInterval(loadOverview, 10000);
    }
    if (tab === 'pipeline') {
      loadActiveAgents();
      agentRefreshTimer = setInterval(loadActiveAgents, 5000);
    }
  });
});

// ----- API Fetch -----
async function apiFetch(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(r.status);
    return await r.json();
  } catch (e) {
    console.error('API error:', url, e);
    return null;
  }
}

// ----- Overview -----
async function loadOverview() {
  const data = await apiFetch('/api/overview');
  if (!data) return;
  overviewData = data;
  const s = data.stats;
  const c = data.config;

  document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

  // Metrics — handle both higher-is-better and lower-is-better
  const dec = c.decimals || 4;
  const hib = c.higher_is_better;
  let pct = 0;
  if (s.best_score != null && c.target_score != null) {
    // Find baseline from initial programs
    const initScores = (data.initial_scores || []).filter(x => x.score != null).map(x => x.score);
    const baseline = initScores.length > 0 ? (hib ? Math.max(...initScores) : Math.min(...initScores)) : (hib ? 0 : s.best_score * 1.5);
    if (hib) {
      pct = c.target_score > 0 ? Math.min(100, (s.best_score / c.target_score) * 100) : 0;
    } else {
      // lower-is-better: progress = how far from baseline toward target
      const range = baseline - c.target_score;
      pct = range > 0 ? Math.min(100, ((baseline - s.best_score) / range) * 100) : 0;
    }
  }
  document.getElementById('bestScoreVal').textContent = s.best_score != null ? s.best_score.toFixed(dec) : '--';
  document.getElementById('scoreBar').style.width = Math.max(0, pct) + '%';
  document.getElementById('scorePercent').textContent = pct.toFixed(1) + '% to target';
  document.getElementById('gaugeTarget').textContent = c.target_score;

  // Gauge arc
  const arc = document.getElementById('gaugeArc');
  const circumference = 2 * Math.PI * 38;
  const offset = circumference - (pct / 100) * circumference;
  arc.setAttribute('stroke-dasharray', circumference);
  arc.setAttribute('stroke-dashoffset', offset);
  document.getElementById('gaugeText').textContent = s.best_score != null ? s.best_score.toFixed(dec) : '--';

  // Gauge color
  const gaugeColor = pct > 80 ? 'var(--accent)' : pct > 40 ? 'var(--amber)' : 'var(--red)';
  arc.setAttribute('stroke', gaugeColor);
  document.getElementById('gaugeText').setAttribute('fill', gaugeColor);
  document.getElementById('bestScoreVal').style.color = gaugeColor;

  document.getElementById('genVal').textContent = s.current_gen || s.completed_gens;
  document.getElementById('genSub').textContent = s.completed_gens < s.current_gen
    ? s.completed_gens + ' done of ' + c.total_generations
    : 'of ' + c.total_generations;
  document.getElementById('solVal').textContent = s.total_solutions;
  document.getElementById('solSub').textContent = s.valid_solutions + ' valid';
  document.getElementById('ideaVal').textContent = s.total_ideas;
  document.getElementById('ideaSub').textContent = s.total_facts + ' facts';
  document.getElementById('knowVal').textContent = s.total_clusters + s.total_patterns;
  document.getElementById('knowSub').textContent = s.total_clusters + ' clusters \u00b7 ' + s.total_patterns + ' patterns';

  // Phase strip — map agents_running to agents_done step for display
  const currentPhase = s.current_phase;
  const displayPhase = currentPhase === 'agents_running' ? 'agents_done' : currentPhase;
  const phaseIdx = PHASE_ORDER.indexOf(currentPhase);
  document.querySelectorAll('.phase-step').forEach(el => {
    const elPhase = el.dataset.phase;
    const elIdx = PHASE_ORDER.indexOf(elPhase);
    el.classList.remove('completed', 'active', 'pending');
    if (elPhase === 'agents_done' && currentPhase === 'agents_running') {
      el.classList.add('active');
    } else if (elIdx < phaseIdx) el.classList.add('completed');
    else if (elIdx === phaseIdx) el.classList.add('active');
    else el.classList.add('pending');
  });

  // Pipeline (if visible)
  updatePipeline(currentPhase);

  // Agent type cards (dynamic from config)
  renderAgentCards(data.agent_types || []);

  // Generation timeline
  const timeline = document.getElementById('genTimeline');
  const emptyTl = document.getElementById('genTimelineEmpty');
  if (data.generations.length === 0) {
    timeline.style.display = 'none';
    emptyTl.style.display = 'block';
  } else {
    timeline.style.display = 'flex';
    emptyTl.style.display = 'none';
    timeline.innerHTML = data.generations.map(g => `
      <div class="gen-card">
        <div class="gen-num">Gen ${g.gen}</div>
        <span class="gen-status ${g.status}">${g.status.replace(/_/g, ' ')}</span>
        <div class="gen-score">${g.best_score !== null ? g.best_score.toFixed(4) : '--'}</div>
        <div class="gen-sols">${g.solutions} sol${g.solutions !== 1 ? 's' : ''}</div>
      </div>
    `).join('');
  }

  // Chart — use score_progression.md data, or synthesize from generation scores
  let chartProgression = data.progression;
  if ((!chartProgression || chartProgression.length === 0) && data.generations.length > 0) {
    chartProgression = data.generations
      .filter(g => g.best_score != null)
      .map(g => ({ gen: g.gen, best_fitness: g.best_score }));
  }
  const initScores = (data.initial_scores || []).filter(x => x.score != null).map(x => x.score);
  let baselineScore = initScores.length > 0 ? (c.higher_is_better ? Math.max(...initScores) : Math.min(...initScores)) : null;
  // Fallback baseline from config if initial programs have no score
  if (baselineScore == null && c.baseline_score != null) baselineScore = c.baseline_score;
  drawChart(chartProgression, c.target_score, c.higher_is_better, baselineScore, c.decimals || 4);
}

function updatePipeline(currentPhase) {
  const phaseIdx = PHASE_ORDER.indexOf(currentPhase);
  document.querySelectorAll('.pipeline-node').forEach(node => {
    const nodePhase = node.dataset.pipePhase;
    const nodeIdx = PHASE_ORDER.indexOf(nodePhase);
    node.classList.remove('active-phase', 'completed-phase');
    if (nodePhase === 'agents_done' && currentPhase === 'agents_running') {
      node.classList.add('active-phase');
    } else if (nodeIdx < phaseIdx) node.classList.add('completed-phase');
    else if (nodeIdx === phaseIdx) node.classList.add('active-phase');
  });

  // Arrows
  for (let i = 1; i <= 5; i++) {
    const arrow = document.getElementById('pa-' + i);
    if (!arrow) continue;
    const prevPhaseIdx = i; // arrow i connects node i to node i+1
    if (prevPhaseIdx < phaseIdx) {
      arrow.classList.add('flow-active');
    } else {
      arrow.classList.remove('flow-active');
    }
  }
}

function renderAgentCards(agentTypes) {
  const grid = document.getElementById('agentsGrid');
  if (!grid || agentTypes.length === 0) return;
  grid.innerHTML = agentTypes.map(a => {
    const label = a.type.charAt(0).toUpperCase() + a.type.slice(1);
    return `
      <div class="agent-card${a.enabled ? '' : ' disabled'}">
        <div class="agent-card-header"><span class="agent-type-badge badge-${a.type}">${label}</span></div>
        <div class="agent-stat"><span>Max Instances</span><span class="agent-stat-val">${a.max_instances}</span></div>
        <div class="agent-stat"><span>Max Turns</span><span class="agent-stat-val">${a.max_turns}</span></div>
        <div class="agent-stat"><span>Model</span><span class="agent-stat-val">${a.model}</span></div>
        <div class="agent-stat"><span>Purpose</span><span class="agent-stat-val" style="color:var(--text-tertiary)">${a.purpose}</span></div>
      </div>`;
  }).join('');
}

// ----- Chart (Canvas) -----
function drawChart(progression, target, higherIsBetter, baseline, decimals) {
  const canvas = document.getElementById('progressionChart');
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = rect.height + 'px';
  ctx.scale(dpr, dpr);
  const W = rect.width, H = rect.height;
  const dec = decimals || 4;

  ctx.clearRect(0, 0, W, H);

  const pad = { top: 20, right: 20, bottom: 30, left: 60 };
  const chartW = W - pad.left - pad.right;
  const chartH = H - pad.top - pad.bottom;

  if ((!progression || progression.length === 0) && baseline == null) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('No data yet \u2014 waiting for first generation', W / 2, H / 2);
    return;
  }

  // Determine Y-axis range from all data points
  const allScores = [
    ...(progression || []).map(p => p.best_fitness),
    ...(target != null ? [target] : []),
    ...(baseline != null ? [baseline] : []),
  ].filter(v => v != null && isFinite(v));

  let minScore = Math.min(...allScores);
  let maxScore = Math.max(...allScores);
  const margin = (maxScore - minScore) * 0.15 || 0.01;
  minScore -= margin;
  maxScore += margin;

  const maxGen = Math.max(...(progression || []).map(p => p.gen), 5);

  function x(gen) { return pad.left + (gen / maxGen) * chartW; }
  function y(score) { return pad.top + chartH - ((score - minScore) / (maxScore - minScore)) * chartH; }

  // Grid lines
  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const yy = pad.top + (i / 5) * chartH;
    ctx.beginPath();
    ctx.moveTo(pad.left, yy);
    ctx.lineTo(W - pad.right, yy);
    ctx.stroke();

    const scoreLabel = (maxScore - (i / 5) * (maxScore - minScore)).toFixed(dec);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(scoreLabel, pad.left - 8, yy + 3);
  }

  // X axis labels
  ctx.textAlign = 'center';
  ctx.fillStyle = '#475569';
  for (let g = 0; g <= maxGen; g += Math.max(1, Math.floor(maxGen / 10))) {
    ctx.fillText('G' + g, x(g), H - 8);
  }

  // Baseline line (initial program)
  if (baseline != null) {
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, y(baseline));
    ctx.lineTo(W - pad.right, y(baseline));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(148, 163, 184, 0.8)';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText('BASELINE ' + baseline.toFixed(dec), pad.left + 5, y(baseline) - 5);
  }

  // Target line
  if (target != null) {
    ctx.strokeStyle = 'rgba(5, 150, 105, 0.35)';
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, y(target));
    ctx.lineTo(W - pad.right, y(target));
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = 'rgba(5, 150, 105, 0.6)';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText('TARGET ' + target.toFixed(dec), W - pad.right - 5, y(target) - 5);
  }

  // "Better" direction arrow
  ctx.fillStyle = '#94a3b8';
  ctx.font = '10px JetBrains Mono, monospace';
  ctx.textAlign = 'left';
  const betterDir = higherIsBetter ? '\u2191 better' : '\u2193 better';
  ctx.fillText(betterDir, pad.left + 5, pad.top + 12);

  if (progression && progression.length > 0) {
    // Gradient fill
    const betterY = higherIsBetter ? y(maxScore) : y(minScore);
    const worseY = higherIsBetter ? y(minScore) : y(maxScore);
    const grad = ctx.createLinearGradient(0, betterY, 0, worseY);
    grad.addColorStop(0, 'rgba(5, 150, 105, 0.15)');
    grad.addColorStop(1, 'rgba(5, 150, 105, 0)');

    if (progression.length > 1) {
      ctx.fillStyle = grad;
      ctx.beginPath();
      const baseY = higherIsBetter ? y(minScore) : y(maxScore);
      ctx.moveTo(x(progression[0].gen), baseY);
      progression.forEach(p => ctx.lineTo(x(p.gen), y(p.best_fitness)));
      ctx.lineTo(x(progression[progression.length - 1].gen), baseY);
      ctx.closePath();
      ctx.fill();
    }

    // Line
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    progression.forEach((p, i) => {
      if (i === 0) ctx.moveTo(x(p.gen), y(p.best_fitness));
      else ctx.lineTo(x(p.gen), y(p.best_fitness));
    });
    ctx.stroke();

    // Points
    progression.forEach(p => {
      ctx.fillStyle = '#059669';
      ctx.beginPath();
      ctx.arc(x(p.gen), y(p.best_fitness), 3, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(x(p.gen), y(p.best_fitness), 1.5, 0, Math.PI * 2);
      ctx.fill();
    });
  }
}

// Resize chart on window resize
window.addEventListener('resize', () => {
  if (overviewData) {
    const c = overviewData.config;
    const initScores = (overviewData.initial_scores || []).filter(x => x.score != null).map(x => x.score);
    let bl = initScores.length > 0 ? (c.higher_is_better ? Math.max(...initScores) : Math.min(...initScores)) : null;
    if (bl == null && c.baseline_score != null) bl = c.baseline_score;
    let prog = overviewData.progression;
    if ((!prog || prog.length === 0) && overviewData.generations.length > 0) {
      prog = overviewData.generations.filter(g => g.best_score != null).map(g => ({ gen: g.gen, best_fitness: g.best_score }));
    }
    drawChart(prog, c.target_score, c.higher_is_better, bl, c.decimals || 4);
  }
});

// ----- Solutions -----
async function loadSolutions() {
  if (!solutionsData) {
    solutionsData = await apiFetch('/api/solutions');
  }
  renderSolutions();
}

function renderSolutions() {
  const data = solutionsData || [];
  const tbody = document.getElementById('solTableBody');
  const empty = document.getElementById('solEmpty');
  const info = document.getElementById('solCountInfo');

  // Populate filter dropdowns
  const gens = [...new Set(data.map(s => s.gen))].sort((a, b) => a - b);
  const agents = [...new Set(data.map(s => s.agent_type))].sort();
  const genSel = document.getElementById('solFilterGen');
  const agentSel = document.getElementById('solFilterAgent');

  if (genSel.options.length <= 1) {
    gens.forEach(g => { const o = new Option('Gen ' + g, g); genSel.add(o); });
  }
  if (agentSel.options.length <= 1) {
    agents.forEach(a => { const o = new Option(a, a); agentSel.add(o); });
  }

  let filtered = data;
  if (solFilterGen !== 'all') filtered = filtered.filter(s => s.gen == solFilterGen);
  if (solFilterAgent !== 'all') filtered = filtered.filter(s => s.agent_type === solFilterAgent);

  // Sort
  filtered.sort((a, b) => {
    let av = a[solSort.key], bv = b[solSort.key];
    if (av == null) av = -99999;
    if (bv == null) bv = -99999;
    if (typeof av === 'string') return av.localeCompare(bv) * solSort.dir;
    return (av - bv) * solSort.dir;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '';
    empty.style.display = 'block';
    info.textContent = '';
    return;
  }

  empty.style.display = 'none';
  info.textContent = filtered.length + ' solution' + (filtered.length !== 1 ? 's' : '');

  tbody.innerHTML = filtered.map(s => {
    const scoreClass = s.score == null ? 'score-none' : '';
    const dec = (overviewData && overviewData.config) ? overviewData.config.decimals || 4 : 4;
    const scoreText = s.score != null ? s.score.toFixed(dec) : '--';
    const validClass = s.is_valid ? 'valid-yes' : 'valid-no';
    const sizeStr = s.size > 1024 ? (s.size / 1024).toFixed(1) + 'K' : s.size + 'B';
    const badgeClass = 'badge-' + s.agent_type;

    const agentLabel = s.agent_type + '_' + s.instance;
    return `<tr>
      <td>${s.gen}</td>
      <td><span class="agent-type-badge ${badgeClass}">${agentLabel}</span></td>
      <td>${s.file}</td>
      <td class="score-cell ${scoreClass}">${scoreText}</td>
      <td><span class="valid-badge ${validClass}"></span></td>
      <td>${sizeStr}</td>
      <td style="color: var(--text-ghost)">${s.modified || ''}</td>
    </tr>`;
  }).join('');
}

// Sort handlers
document.querySelectorAll('.sol-table th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (solSort.key === key) solSort.dir *= -1;
    else { solSort.key = key; solSort.dir = key === 'score' ? -1 : 1; }

    document.querySelectorAll('.sol-table th').forEach(h => {
      h.classList.remove('sort-active');
      h.querySelector('.sort-arrow').textContent = '';
    });
    th.classList.add('sort-active');
    th.querySelector('.sort-arrow').textContent = solSort.dir > 0 ? '\u25B2' : '\u25BC';
    renderSolutions();
  });
});

document.getElementById('solFilterGen').addEventListener('change', e => { solFilterGen = e.target.value; renderSolutions(); });
document.getElementById('solFilterAgent').addEventListener('change', e => { solFilterAgent = e.target.value; renderSolutions(); });

// ----- Knowledge -----
async function loadKnowledge() {
  const data = await apiFetch('/api/knowledge');
  if (!data) return;
  knowledgeData = data;

  // State of Affairs
  document.getElementById('soaContent').textContent = data.state_of_affairs || 'No state of affairs written yet.';
  const meta = data.state_of_affairs_meta || {};
  document.getElementById('soaMeta').innerHTML = [
    meta.generation != null ? `<span class="soa-meta-item">Gen: <span>${meta.generation}</span></span>` : '',
    meta.best_score != null ? `<span class="soa-meta-item">Best: <span>${meta.best_score}</span></span>` : '',
    meta.trajectory ? `<span class="soa-meta-item">Trajectory: <span>${meta.trajectory}</span></span>` : '',
  ].join('');

  renderIdeas();

  // Facts
  const factsList = document.getElementById('factsList');
  if (data.facts.length === 0) {
    factsList.innerHTML = '<div class="empty-state" style="padding:20px"><div class="empty-desc">No facts recorded</div></div>';
  } else {
    factsList.innerHTML = data.facts.map(f => `
      <div class="fact-item clickable" onclick="openKnowledgeModal('fact', '${escAttr(f.id)}')">
        <div class="fact-icon">${f.critical ? '&#9888;' : '&#9679;'}</div>
        <div class="fact-content">
          <div class="fact-title">${esc(f.title)}</div>
          <div class="fact-body">${esc(f.body)}</div>
        </div>
      </div>
    `).join('');
  }

  // Patterns
  const patList = document.getElementById('patternsList');
  const patEmpty = document.getElementById('patternsEmpty');
  if (data.patterns.length === 0) {
    patList.innerHTML = '';
    patEmpty.style.display = 'block';
  } else {
    patEmpty.style.display = 'none';
    patList.innerHTML = data.patterns.map(p => `
      <div class="fact-item clickable" onclick="openKnowledgeModal('pattern', '${escAttr(p.id)}')">
        <div class="fact-icon">&#9670;</div>
        <div class="fact-content">
          <div class="fact-title">${esc(p.title)} <span class="lifecycle-badge lc-${p.lifecycle}">${p.lifecycle}</span></div>
          <div class="fact-body">${esc(p.body)}</div>
        </div>
      </div>
    `).join('');
  }

  // Clusters
  const cluList = document.getElementById('clustersList');
  const cluEmpty = document.getElementById('clustersEmpty');
  if (data.clusters.length === 0) {
    cluList.innerHTML = '';
    cluEmpty.style.display = 'block';
  } else {
    cluEmpty.style.display = 'none';
    cluList.innerHTML = data.clusters.map(c => `
      <div class="fact-item clickable" onclick="openKnowledgeModal('cluster', '${escAttr(c.id)}')">
        <div class="fact-icon" style="color: var(--blue)">&#9673;</div>
        <div class="fact-content">
          <div class="fact-title">${esc(c.title)} ${c.idea_count ? '<span style="font-size:0.65rem;color:var(--text-ghost)">' + c.idea_count + ' ideas</span>' : ''}</div>
          <div class="fact-body">${esc(c.body)}</div>
        </div>
      </div>
    `).join('');
  }
}

function renderIdeas() {
  if (!knowledgeData) return;
  const grid = document.getElementById('ideasGrid');
  const empty = document.getElementById('ideasEmpty');

  let ideas = knowledgeData.ideas;
  if (ideaFilterLc !== 'all') ideas = ideas.filter(i => i.lifecycle === ideaFilterLc);

  if (ideas.length === 0) {
    grid.innerHTML = '';
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';
  grid.innerHTML = ideas.map(i => `
    <div class="idea-card clickable" onclick="openKnowledgeModal('idea', '${escAttr(i.id)}')">
      <div class="idea-card-top">
        <span class="idea-id">${esc(i.id)}</span>
        <span class="lifecycle-badge lc-${i.lifecycle}">${i.lifecycle}</span>
      </div>
      <div class="idea-title">${esc(i.title)}</div>
      <div class="idea-body">${esc(i.body)}</div>
      <div class="idea-stats">
        <span class="idea-stat">confidence: <span>${esc(String(i.confidence))}</span></span>
        <span class="idea-stat">gen: <span>${esc(String(i.first_seen))}</span></span>
        ${i.cluster ? `<span class="idea-stat">cluster: <span>${esc(String(i.cluster))}</span></span>` : ''}
      </div>
    </div>
  `).join('');
}

// Idea lifecycle filter
document.getElementById('ideasControls').addEventListener('click', e => {
  if (!e.target.classList.contains('lc-filter-btn')) return;
  document.querySelectorAll('.lc-filter-btn').forEach(b => b.classList.remove('active'));
  e.target.classList.add('active');
  ideaFilterLc = e.target.dataset.lc;
  renderIdeas();
});

// ----- Reports -----
async function loadReports() {
  const data = await apiFetch('/api/reports');
  if (!data) return;
  reportsData = data;

  const list = document.getElementById('reportsList');
  const empty = document.getElementById('reportsEmpty');

  if (data.length === 0) {
    list.innerHTML = '';
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';

  // Group by generation
  const byGen = {};
  data.forEach(r => {
    if (!byGen[r.gen]) byGen[r.gen] = [];
    byGen[r.gen].push(r);
  });

  let html = '';
  Object.keys(byGen).sort((a, b) => b - a).forEach(gen => {
    byGen[gen].forEach(r => {
      const agentType = r.agent.split('_')[0];
      const badgeClass = 'badge-' + agentType;
      const sizeStr = r.size > 1024 ? (r.size / 1024).toFixed(1) + 'K' : r.size + 'B';

      html += `
        <div class="report-item">
          <div class="report-header" onclick="this.parentElement.classList.toggle('open')">
            <span class="report-toggle">&#9654;</span>
            <span class="report-gen-badge">Gen ${r.gen}</span>
            <span class="agent-type-badge ${badgeClass}" style="font-size:0.62rem">${agentType}</span>
            <span class="report-agent-name">${esc(r.agent)}</span>
            <span class="report-size">${sizeStr}</span>
          </div>
          <div class="report-content">
            <div class="report-body">${esc(r.content)}</div>
          </div>
        </div>
      `;
    });
  });
  list.innerHTML = html;
}

// ----- Files -----
async function loadFiles() {
  const data = await apiFetch('/api/files');
  if (!data) return;
  filesData = data;

  const tree = document.getElementById('fileTree');
  const dirColors = {
    population: 'dir-population',
    knowledge: 'dir-knowledge',
    reports: 'dir-reports',
    briefs: 'dir-briefs',
    feedback: 'dir-feedback',
    history: 'dir-history',
    agents: 'dir-agents',
    problem: 'dir-problem',
    user: 'dir-user',
  };

  const dirIcons = {
    population: '&#128202;',
    knowledge: '&#128218;',
    reports: '&#128220;',
    briefs: '&#128231;',
    feedback: '&#128172;',
    history: '&#128197;',
    agents: '&#129302;',
    problem: '&#128300;',
    user: '&#128100;',
  };

  let html = '';
  for (const [dirName, files] of Object.entries(data)) {
    const colorClass = dirColors[dirName] || '';

    // Group files by subdirectory
    const subDirs = {};
    files.forEach(f => {
      const parts = f.path.split('/');
      const sub = parts.length > 2 ? parts.slice(1, -1).join('/') : '.';
      if (!subDirs[sub]) subDirs[sub] = [];
      subDirs[sub].push(f);
    });

    html += `
      <div class="tree-dir ${colorClass}">
        <div class="tree-dir-header" onclick="this.parentElement.classList.toggle('open')">
          <span class="tree-toggle">&#9654;</span>
          <span class="tree-dir-icon">${dirIcons[dirName] || '&#128193;'}</span>
          <span class="tree-dir-name">${dirName}/</span>
          <span class="tree-dir-count">${files.length} file${files.length !== 1 ? 's' : ''}</span>
        </div>
        <div class="tree-files">
    `;

    for (const [sub, subFiles] of Object.entries(subDirs)) {
      if (sub !== '.') {
        html += `<div style="font-size:0.65rem;color:var(--text-ghost);padding:6px 0 2px;margin-top:4px;border-top:1px solid var(--border);">${sub}/</div>`;
      }
      subFiles.forEach(f => {
        const sizeStr = f.size > 1024 ? (f.size / 1024).toFixed(1) + 'K' : f.size + 'B';
        html += `<div class="tree-file">
          <span style="color: var(--text-ghost)">&#9702;</span>
          <span>${esc(f.name)}</span>
          <span class="tree-file-size">${sizeStr}</span>
        </div>`;
      });
    }

    html += `</div></div>`;
  }

  tree.innerHTML = html || '<div class="empty-state" style="padding:20px"><div class="empty-desc">No files found</div></div>';
}

// ----- Utilities -----
function esc(s) {
  if (s == null) return '';
  const d = document.createElement('div');
  d.textContent = String(s);
  return d.innerHTML;
}

function escAttr(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ----- Live Agents -----
async function loadActiveAgents() {
  const data = await apiFetch('/api/agents/active');
  if (!data) return;
  activeAgentsData = data;

  const container = document.getElementById('liveAgentsContainer');
  const empty = document.getElementById('liveAgentsEmpty');
  const status = document.getElementById('liveAgentStatus');

  if (!container) return;

  if (data.length === 0) {
    container.innerHTML = '';
    container.appendChild(empty);
    empty.style.display = 'block';
    status.textContent = 'No active sessions';
    return;
  }

  empty.style.display = 'none';
  const running = data.filter(a => a.status !== 'completed').length;
  const done = data.filter(a => a.status === 'completed').length;
  status.textContent = running > 0
    ? running + ' running' + (done > 0 ? ', ' + done + ' done' : '')
    : done + ' completed';

  const dec = (overviewData && overviewData.config) ? overviewData.config.decimals || 4 : 4;

  container.innerHTML = data.map(a => {
    const statusClass = 'agent-' + a.status;
    const scoreText = a.best_score != null ? a.best_score.toFixed(dec) : '--';
    const badgeClass = 'badge-' + a.agent_type;
    const label = a.agent_type + '_' + a.instance;

    let solChips = '';
    if (a.solutions && a.solutions.length > 0) {
      solChips = a.solutions.map(s => {
        const cls = s.is_valid ? 'valid' : (s.score != null ? 'invalid' : '');
        const txt = s.file + (s.score != null ? ': ' + s.score.toFixed(dec) : '');
        return `<span class="live-agent-sol-chip ${cls}">${esc(txt)}</span>`;
      }).join('');
    }

    return `
      <div class="live-agent-panel ${statusClass}" onclick="this.classList.toggle('expanded')">
        <div class="live-agent-header">
          <div class="live-agent-status-dot"></div>
          <span class="agent-type-badge ${badgeClass}">${esc(a.agent_type)}</span>
          <span class="live-agent-name">${esc(label)}</span>
          <span class="live-agent-gen-badge">Gen ${a.gen}</span>
          <span class="live-agent-status-label">${esc(a.status)}</span>
          <span class="live-agent-expand-toggle">&#9654;</span>
        </div>
        <div class="live-agent-body">
          ${a.brief_snippet ? `<div class="live-agent-brief">${esc(a.brief_snippet)}</div>` : ''}
          <div class="live-agent-stats">
            <span class="live-agent-stat">Solutions: <span>${a.solution_count}</span></span>
            <span class="live-agent-stat">Best: <span>${scoreText}</span></span>
            ${a.has_report ? '<span class="live-agent-stat" style="color:var(--accent)">Report written</span>' : ''}
            ${a.has_observations ? '<span class="live-agent-stat">Has observations</span>' : ''}
          </div>
          ${solChips ? `<div class="live-agent-solutions"><div class="live-agent-sol-bar">${solChips}</div></div>` : ''}
        </div>
        <div class="live-agent-details">
          <div class="live-agent-detail-content">
            ${a.solutions.length > 0 ? `
              <table class="live-agent-sol-table">
                <thead><tr><th>File</th><th>Score</th><th>Valid</th></tr></thead>
                <tbody>
                  ${a.solutions.map(s => `<tr>
                    <td>${esc(s.file)}</td>
                    <td style="font-weight:600">${s.score != null ? s.score.toFixed(dec) : '--'}</td>
                    <td>${s.is_valid ? '<span style="color:var(--accent)">Yes</span>' : '<span style="color:var(--text-ghost)">No</span>'}</td>
                  </tr>`).join('')}
                </tbody>
              </table>
            ` : '<div style="font-size:0.7rem;color:var(--text-ghost)">No solutions written yet</div>'}
            <div style="font-size:0.62rem;color:var(--text-ghost);margin-top:8px">Last modified: ${esc(a.last_modified)}</div>
          </div>
        </div>
      </div>`;
  }).join('');
}

// ----- Knowledge Detail Modal -----
const modalOverlay = document.getElementById('modalOverlay');
const modalPanel = document.getElementById('modalPanel');
const modalClose = document.getElementById('modalClose');
const modalTitle = document.getElementById('modalTitle');
const modalKindBadge = document.getElementById('modalKindBadge');
const modalMeta = document.getElementById('modalMeta');
const modalBody = document.getElementById('modalBody');
const modalFooter = document.getElementById('modalFooter');

function openModal(kind, data) {
  const kindLabels = { idea: 'Idea', fact: 'Fact', pattern: 'Pattern', cluster: 'Cluster' };
  modalKindBadge.textContent = kindLabels[kind] || kind;
  modalKindBadge.className = 'modal-kind-badge kind-' + kind;
  modalTitle.textContent = data.title || data.id || 'Untitled';

  let metaHtml = '';
  if (kind === 'idea') {
    metaHtml += `<span class="modal-meta-item"><strong>Lifecycle:</strong> <span class="lifecycle-badge lc-${data.lifecycle}">${data.lifecycle}</span></span>`;
    metaHtml += `<span class="modal-meta-item"><strong>Confidence:</strong> ${esc(String(data.confidence))}</span>`;
    metaHtml += `<span class="modal-meta-item"><strong>First seen:</strong> ${esc(String(data.first_seen))}</span>`;
    if (data.last_confirmed_gen && data.last_confirmed_gen !== '?') {
      metaHtml += `<span class="modal-meta-item"><strong>Last confirmed:</strong> Gen ${esc(String(data.last_confirmed_gen))}</span>`;
    }
    if (data.cluster) {
      metaHtml += `<span class="modal-meta-item"><strong>Cluster:</strong> ${esc(String(data.cluster))}</span>`;
    }
  } else if (kind === 'fact') {
    metaHtml += `<span class="modal-meta-item"><strong>Confidence:</strong> ${esc(String(data.confidence))}</span>`;
    metaHtml += `<span class="modal-meta-item"><strong>Verified:</strong> ${data.verified ? 'Yes' : 'No'}</span>`;
    metaHtml += `<span class="modal-meta-item"><strong>First seen:</strong> ${esc(String(data.first_seen))}</span>`;
  } else if (kind === 'pattern') {
    metaHtml += `<span class="modal-meta-item"><strong>Lifecycle:</strong> <span class="lifecycle-badge lc-${data.lifecycle}">${data.lifecycle}</span></span>`;
  } else if (kind === 'cluster') {
    if (data.idea_count != null) metaHtml += `<span class="modal-meta-item"><strong>Ideas:</strong> ${data.idea_count}</span>`;
    metaHtml += `<span class="modal-meta-item"><strong>Status:</strong> ${esc(data.status || '?')}</span>`;
  }
  metaHtml += `<span class="modal-meta-item"><strong>ID:</strong> ${esc(data.id || '?')}</span>`;
  modalMeta.innerHTML = metaHtml;

  modalBody.textContent = data.body || 'No content.';

  // Footer: tags for relationships
  let footerHtml = '';
  if (data.supported_by && data.supported_by.length > 0) {
    footerHtml += data.supported_by.map(s => `<span class="modal-tag" style="border-left:3px solid var(--accent);padding-left:6px">Supported: ${esc(String(s))}</span>`).join('');
  }
  if (data.contradicted_by && data.contradicted_by.length > 0) {
    footerHtml += data.contradicted_by.map(s => `<span class="modal-tag" style="border-left:3px solid var(--red);padding-left:6px">Contradicted: ${esc(String(s))}</span>`).join('');
  }
  if (data.related_ideas && data.related_ideas.length > 0) {
    footerHtml += data.related_ideas.map(s => `<span class="modal-tag" style="border-left:3px solid var(--blue);padding-left:6px">Related: ${esc(String(s))}</span>`).join('');
  }
  if (data.member_ideas && data.member_ideas.length > 0) {
    footerHtml += data.member_ideas.map(s => `<span class="modal-tag" style="border-left:3px solid var(--purple);padding-left:6px">Member: ${esc(String(s))}</span>`).join('');
  }
  modalFooter.innerHTML = footerHtml;

  modalOverlay.classList.add('visible');
}

function closeModal() {
  modalOverlay.classList.remove('visible');
}

modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', e => {
  if (e.target === modalOverlay) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// Open modal from locally cached knowledge data (no extra API call needed)
function openKnowledgeModal(kind, itemId) {
  if (!knowledgeData) return;

  let item = null;
  if (kind === 'idea') {
    item = knowledgeData.ideas.find(i => i.id === itemId);
  } else if (kind === 'fact') {
    item = knowledgeData.facts.find(f => f.id === itemId);
  } else if (kind === 'pattern') {
    item = knowledgeData.patterns.find(p => p.id === itemId);
  } else if (kind === 'cluster') {
    item = knowledgeData.clusters.find(c => c.id === itemId);
  }

  if (item) {
    openModal(kind, item);
  }
}

// ----- Init -----
loadOverview();
refreshTimer = setInterval(loadOverview, 10000);
