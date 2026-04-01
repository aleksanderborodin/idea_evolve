// ======================================================================
// Idea Evolve Dashboard — Client Logic
// ======================================================================

// --- Context Management (problem/attempt selection) ---
let currentProblem = localStorage.getItem('ie_problem') || null;
let currentAttempt = localStorage.getItem('ie_attempt') || null;
let problemsCache = null;

// Clean up legacy values from old versions
if (currentProblem === 'default') { currentProblem = null; localStorage.removeItem('ie_problem'); }
if (currentAttempt === 'legacy') { currentAttempt = null; localStorage.removeItem('ie_attempt'); }

function getApiParams() {
  const params = new URLSearchParams();
  if (currentProblem && currentProblem !== 'default') params.set('problem', currentProblem);
  if (currentAttempt && currentAttempt !== 'legacy') params.set('attempt', currentAttempt);
  return params.toString() ? '?' + params.toString() : '';
}

function setContext(problem, attempt) {
  currentProblem = problem;
  currentAttempt = attempt;
  if (problem) localStorage.setItem('ie_problem', problem);
  else localStorage.removeItem('ie_problem');
  if (attempt) localStorage.setItem('ie_attempt', attempt);
  else localStorage.removeItem('ie_attempt');
  updateContextBreadcrumb();
  overviewData = null;
  solutionsData = null;
  knowledgeData = null;
  reportsData = null;
  filesData = null;
  const activeTab = document.querySelector('.nav-tab.active');
  if (activeTab) activeTab.click();
}

function updateContextBreadcrumb() {
  const probEl = document.getElementById('ctxProblem');
  const attEl = document.getElementById('ctxAttempt');
  const dotEl = document.getElementById('ctxDot');
  if (probEl) probEl.textContent = currentProblem || '--';
  if (attEl) attEl.textContent = currentAttempt || 'no attempts';
  if (dotEl && problemsCache) {
    const prob = problemsCache.find(p => p.id === currentProblem);
    if (prob) {
      const att = prob.attempts.find(a => a.id === currentAttempt);
      const status = att ? att.status : 'idle';
      dotEl.className = 'ctx-status-dot ' + status;
    }
  }
}

function openFlyout() {
  const overlay = document.getElementById('flyoutOverlay');
  if (overlay) { overlay.classList.add('open'); loadProblems(); }
}

function closeFlyout() {
  const overlay = document.getElementById('flyoutOverlay');
  if (overlay) overlay.classList.remove('open');
}

async function loadProblems() {
  const body = document.getElementById('flyoutBody');
  if (!body) return;
  body.innerHTML = '<div class="flyout-loading">Loading...</div>';
  try {
    const r = await fetch('/api/problems');
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    problemsCache = data;
    updateContextBreadcrumb();
    renderFlyoutBody(data);
  } catch (e) {
    body.innerHTML = '<div class="flyout-loading">Failed to load problems</div>';
  }
}

function renderFlyoutBody(problems) {
  const body = document.getElementById('flyoutBody');
  if (!body) return;
  if (!problems.length) { body.innerHTML = '<div class="flyout-loading">No problems found</div>'; return; }

  body.innerHTML = problems.map(p => {
    const attCount = p.attempts.length;
    const isExp = problems.length === 1 || p.id === currentProblem;
    return `
      <div class="flyout-problem${isExp ? ' expanded' : ''}" data-problem="${p.id}">
        <div class="flyout-problem-header" onclick="toggleFlyoutProblem(this)">
          <span class="flyout-problem-chevron">&#9654;</span>
          <span class="flyout-problem-name">${escHtml(p.name)}</span>
          <span class="flyout-problem-meta">${attCount} attempt${attCount !== 1 ? 's' : ''}</span>
        </div>
        ${p.description_first_line ? `<div class="flyout-problem-desc">${escHtml(p.description_first_line)}</div>` : ''}
        <div class="flyout-attempts">
          ${p.attempts.map(a => {
            const isActive = p.id === currentProblem && a.id === currentAttempt;
            const scoreStr = a.best_score != null ? a.best_score.toFixed(p.decimals) : '--';
            return `
              <div class="flyout-attempt${isActive ? ' active' : ''}"
                   onclick="selectAttempt('${p.id}', '${a.id}')">
                <span class="flyout-attempt-dot ${a.status}"></span>
                <span class="flyout-attempt-name">${escHtml(a.id)}</span>
                <span class="flyout-attempt-stats">
                  <span class="flyout-attempt-score">${scoreStr}</span><br>
                  Gen ${a.generations_completed} &middot; ${a.total_solutions} sol
                </span>
              </div>`;
          }).join('')}
        </div>
      </div>`;
  }).join('');
}

function toggleFlyoutProblem(headerEl) {
  const el = headerEl.closest('.flyout-problem');
  if (el) el.classList.toggle('expanded');
}

function selectAttempt(problemId, attemptId) {
  setContext(problemId, attemptId);
  closeFlyout();
}

function escHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('contextBtn');
  if (btn) btn.addEventListener('click', openFlyout);
  const closeBtn = document.getElementById('flyoutClose');
  if (closeBtn) closeBtn.addEventListener('click', closeFlyout);
  const overlay = document.getElementById('flyoutOverlay');
  if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) closeFlyout(); });
  updateContextBreadcrumb();
  // Auto-detect context: pick first problem with attempts, or just first problem
  fetch('/api/problems').then(r => r.json()).then(data => {
    problemsCache = data;
    if (data.length > 0 && !currentProblem) {
      // Prefer a problem that has attempts with data
      const withAttempts = data.find(p => p.attempts.length > 0);
      const pick = withAttempts || data[0];
      currentProblem = pick.id;
      currentAttempt = pick.attempts.length > 0 ? pick.attempts[0].id : null;
      localStorage.setItem('ie_problem', currentProblem);
      if (currentAttempt) localStorage.setItem('ie_attempt', currentAttempt);
      else localStorage.removeItem('ie_attempt');
    }
    // Validate stored context still exists
    if (currentProblem && data.length > 0) {
      const prob = data.find(p => p.id === currentProblem);
      if (!prob) {
        currentProblem = data[0].id;
        currentAttempt = data[0].attempts.length > 0 ? data[0].attempts[0].id : null;
        localStorage.setItem('ie_problem', currentProblem);
        if (currentAttempt) localStorage.setItem('ie_attempt', currentAttempt);
        else localStorage.removeItem('ie_attempt');
      } else if (currentAttempt) {
        const att = prob.attempts.find(a => a.id === currentAttempt);
        if (!att && prob.attempts.length > 0) {
          currentAttempt = prob.attempts[0].id;
          localStorage.setItem('ie_attempt', currentAttempt);
        } else if (!att) {
          currentAttempt = null;
          localStorage.removeItem('ie_attempt');
        }
      }
    }
    updateContextBreadcrumb();
  }).catch(() => {});
});
// --- End Context Management ---

const PHASE_ORDER = ['not_started', 'planned', 'agents_running', 'agents_done', 'evaluator_running', 'evaluator_done', 'critic_running', 'critic_done', 'consistency_running', 'consistency_done', 'complete'];

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

// ----- Dynamic Refresh -----
function getRefreshInterval() {
  if (overviewData?.run_state?.is_running) return 10000;  // 10s when active
  return 60000;  // 60s when idle
}

function rescheduleRefresh(loader, timerName) {
  if (timerName === 'refresh') {
    clearInterval(refreshTimer);
    refreshTimer = setInterval(loader, getRefreshInterval());
  } else {
    clearInterval(agentRefreshTimer);
    agentRefreshTimer = setInterval(loader, getRefreshInterval());
  }
}

// ----- Helpers -----
function timeSince(isoStr) {
  if (!isoStr) return '--';
  const ms = Date.now() - new Date(isoStr).getTime();
  const s = Math.floor(ms / 1000);
  if (s < 60) return s + 's';
  const m = Math.floor(s / 60);
  if (m < 60) return m + 'm ' + (s % 60) + 's';
  const h = Math.floor(m / 60);
  return h + 'h ' + (m % 60) + 'm';
}

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
      refreshTimer = setInterval(loadOverview, getRefreshInterval());
    }
    if (tab === 'pipeline') {
      loadActiveAgents();
      agentRefreshTimer = setInterval(loadActiveAgents, getRefreshInterval());
    }
  });
});

// ----- API Fetch (auto-appends problem/attempt context) -----
async function apiFetch(url) {
  try {
    const ctxParams = getApiParams();
    const fullUrl = ctxParams ? url + (url.includes('?') ? '&' + ctxParams.slice(1) : ctxParams) : url;
    const r = await fetch(fullUrl);
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    const el = document.getElementById('lastUpdate');
    if (el) el.textContent = new Date().toLocaleTimeString();
    return data;
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

  // Metrics — handle both higher-is-better and lower-is-better
  const dec = c.decimals || 4;
  const hib = c.higher_is_better;
  const sentinel = c.sentinel_value;
  let pct = 0;
  if (s.best_score != null && c.target_score != null) {
    // Find baseline from initial programs (exclude sentinel)
    const initScores = (data.initial_scores || []).filter(x => x.score != null && x.score !== sentinel).map(x => x.score);
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

  // Status beacon + system status from run_state
  updateBeacon(data.run_state);
  renderSystemStatus(data.run_state);
  rescheduleRefresh(loadOverview, 'refresh');

  // Phase strip — map *_running to the corresponding step as active
  const currentPhase = s.current_phase;
  const phaseIdx = PHASE_ORDER.indexOf(currentPhase);
  // Map running states to the phase-step they belong to
  const runningToStep = {
    agents_running: 'agents_done',
    evaluator_running: 'evaluator_done',
    critic_running: 'critic_done',
    consistency_running: 'consistency_done',
  };
  const activeStep = runningToStep[currentPhase] || currentPhase;
  document.querySelectorAll('.phase-step').forEach(el => {
    const elPhase = el.dataset.phase;
    const elIdx = PHASE_ORDER.indexOf(elPhase);
    el.classList.remove('completed', 'active', 'pending');
    if (elPhase === activeStep) {
      el.classList.add('active');
    } else if (elIdx < phaseIdx) el.classList.add('completed');
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
    const statusLabels = {
      not_started: 'waiting', planned: 'planned',
      agents_running: 'agents running', agents_done: 'agents done',
      evaluator_running: 'evaluator', evaluator_done: 'evaluator done',
      critic_running: 'critic', critic_done: 'critic done',
      consistency_running: 'consistency', consistency_done: 'consistency done',
      complete: 'complete',
    };
    timeline.innerHTML = data.generations.map(g => {
      const statusText = statusLabels[g.status] || g.status.replace(/_/g, ' ');
      const isRunning = g.status.endsWith('_running') || g.status === 'planned';
      const statusClass = isRunning ? 'agents_running' : g.status;
      return `
      <div class="gen-card">
        <div class="gen-num">Gen ${g.gen}</div>
        <span class="gen-status ${statusClass}">${statusText}</span>
        <div class="gen-score">${g.best_score !== null ? g.best_score.toFixed(dec) : '--'}</div>
        <div class="gen-sols">${g.solutions} sol${g.solutions !== 1 ? 's' : ''}</div>
      </div>`;
    }).join('');
  }

  // Chart — eagerly load solutions for scatter plot, then redraw
  if (!solutionsData) {
    apiFetch('/api/solutions').then(sols => {
      if (sols) solutionsData = sols;
      redrawChart();
    });
  } else {
    redrawChart();
  }

  // Refresh frontier data if frontier is toggled on
  if (showFrontier) {
    apiFetch('/api/frontier').then(data => {
      if (data && data.frontier) {
        frontierData = data.frontier;
        redrawChart();
      }
    });
  }
}

function updatePipeline(currentPhase) {
  const runningToStep = {
    agents_running: 'agents_done',
    evaluator_running: 'evaluator_done',
    critic_running: 'critic_done',
    consistency_running: 'consistency_done',
  };
  const activeStep = runningToStep[currentPhase] || currentPhase;
  const phaseIdx = PHASE_ORDER.indexOf(currentPhase);

  // Pipeline node order maps to PHASE_ORDER done-states
  const nodePhases = ['planned', 'agents_done', 'evaluator_done', 'critic_done', 'consistency_done', 'complete'];

  document.querySelectorAll('.pipeline-node').forEach(node => {
    const nodePhase = node.dataset.pipePhase;
    const nodeIdx = PHASE_ORDER.indexOf(nodePhase);
    node.classList.remove('active-phase', 'completed-phase');
    if (nodePhase === activeStep) {
      node.classList.add('active-phase');
    } else if (nodeIdx < phaseIdx) {
      node.classList.add('completed-phase');
    }
  });

  // Arrows — activate arrows leading up to the active node
  const activeNodeIdx = nodePhases.indexOf(activeStep);
  for (let i = 1; i <= 5; i++) {
    const arrow = document.getElementById('pa-' + i);
    if (!arrow) continue;
    if (i <= activeNodeIdx) {
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

// ----- Status Beacon & System Status -----
function updateBeacon(rs) {
  const beacon = document.getElementById('statusBeacon');
  if (!beacon) return;
  if (rs && rs.is_running) {
    beacon.className = 'status-beacon running';
    beacon.title = `Orchestrator running (gen ${rs.current_gen || '?'}, ${rs.current_phase || '?'})`;
  } else if (rs && rs.available && rs.pid_alive && rs.is_stale) {
    beacon.className = 'status-beacon stale';
    beacon.title = 'Orchestrator may be stuck (no update in >2min)';
  } else if (rs && rs.available && !rs.pid_alive && rs.status === 'running') {
    beacon.className = 'status-beacon crashed';
    beacon.title = 'Orchestrator process died unexpectedly';
  } else {
    beacon.className = 'status-beacon idle';
    beacon.title = rs && rs.available ? 'Orchestrator idle' : 'No run state available';
  }
}

function renderSystemStatus(rs) {
  const el = document.getElementById('systemStatus');
  if (!el) return;
  if (!rs || !rs.available) {
    el.innerHTML = '<span class="sys-status-label idle">No run data</span>';
    return;
  }

  let statusClass, statusLabel;
  if (rs.is_running) { statusClass = 'running'; statusLabel = 'Running'; }
  else if (rs.pid_alive && rs.is_stale) { statusClass = 'stale'; statusLabel = 'Stale'; }
  else if (!rs.pid_alive && rs.status === 'running') { statusClass = 'crashed'; statusLabel = 'Crashed'; }
  else { statusClass = 'idle'; statusLabel = 'Idle'; }

  const phase = rs.current_phase ? rs.current_phase.replace(/_/g, ' ') : '--';
  const elapsed = rs.started_at ? timeSince(rs.started_at) : '--';
  const lastUpdate = rs.age_seconds != null ? Math.round(rs.age_seconds) + 's ago' : '--';
  const gen = rs.current_gen || '--';
  const errors = (rs.errors || []).length;

  el.innerHTML = `
    <div class="sys-status-dot ${statusClass}"></div>
    <div class="sys-status-info">
      <span class="sys-status-label ${statusClass}">${statusLabel}</span>
      <span class="sys-status-detail">Gen ${gen}</span>
      <span class="sys-status-phase">${phase}</span>
      <span class="sys-status-meta">${elapsed} elapsed &middot; updated ${lastUpdate}</span>
      ${errors > 0 ? `<span class="sys-status-errors">${errors} error${errors > 1 ? 's' : ''}</span>` : ''}
    </div>
  `;
}

function renderRunStateAgents(rsAgents) {
  // Merge run_state agent info into live agents display
  const container = document.getElementById('runStateAgents');
  if (!container) return;
  if (!rsAgents || Object.keys(rsAgents).length === 0) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';

  const entries = Object.entries(rsAgents);
  const html = entries.map(([name, info]) => {
    const status = info.status || 'unknown';
    const elapsed = info.started_at ? timeSince(info.started_at) : '';
    const solCount = info.solutions != null ? info.solutions + ' sol' : '';
    const detail = [elapsed, solCount].filter(Boolean).join(' · ');
    return `
      <div class="rs-agent-row">
        <span class="rs-agent-dot ${status}"></span>
        <span class="rs-agent-name">${esc(name)}</span>
        <span class="rs-agent-status">${status.replace(/_/g, ' ')}</span>
        ${detail ? `<span class="rs-agent-detail">${detail}</span>` : ''}
      </div>`;
  }).join('');

  container.innerHTML = `
    <div class="section-header" style="margin-bottom:8px">
      <span class="section-title" style="font-size:0.78rem">Agent Status (from orchestrator)</span>
    </div>
    ${html}`;
}

function renderPipelineErrors(errors) {
  const container = document.getElementById('pipelineErrors');
  if (!container) return;
  if (!errors || errors.length === 0) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';
  const recent = errors.slice(-10).reverse();
  const html = recent.map(e => `
    <div class="pipeline-error-item">
      <span class="pipeline-error-ts">${e.ts ? new Date(e.ts).toLocaleTimeString() : '?'}</span>
      <span class="pipeline-error-gen">Gen ${e.gen || '?'}</span>
      <span class="pipeline-error-phase">${esc(e.phase || '')}</span>
      <span class="pipeline-error-agent">${esc(e.agent || '')}</span>
      <span class="pipeline-error-type ${e.type === 'timeout' ? 'warn' : 'err'}">${esc(e.type || 'error')}</span>
      <span class="pipeline-error-msg">${esc((e.message || '').substring(0, 120))}</span>
    </div>
  `).join('');
  document.getElementById('pipelineErrorsList').innerHTML = html;
}

// =====================================================================
// Chart System — Layered score progression with interactive tooltips
// =====================================================================
//
// Architecture:
//   1. buildChartData()  — transforms raw solutions + progression into
//      structured layers: allPoints, genBests, runningBest, records
//   2. drawChart()       — renders layers bottom-up on canvas:
//      Grid > Baseline > Target > Scatter > GenBest > BestLine > Records
//   3. chartHitTest()    — finds nearest point to mouse for tooltips
//   4. Event listeners   — mousemove (tooltip), click (select), mouseleave (hide)
//
// Data flow:
//   /api/solutions → allPoints[]   (every solution as a dot)
//   /api/overview  → progression[] (gen-level bests, used if solutions unavailable)
//   Config         → target, baseline, direction, sentinel, decimals
//
// Each point: { gen, score, agent, file, isGenBest, isRecord, px, py }
// px/py are set during render for hit testing without recomputing.
//
// Extending:
//   - Add layers by adding a draw function in drawChart() render sequence
//   - Add data by extending buildChartData() return object
//   - Hit regions are point-based; for area hits, extend chartHitTest()
// =====================================================================

let chartPoints = [];      // All rendered points with px/py for hit testing
let chartState = null;     // Last render state for reuse (axes, padding, etc.)
let selectedPoint = null;  // Currently clicked point
let zoomState = { mode: 'auto', yMin: null, yMax: null };
let showFrontier = false;  // Frontier annotation toggle
let frontierData = null;   // Cached frontier data from /api/frontier

function computeAutoRange(scores, target, baseline) {
  const vals = scores.filter(v => v != null && isFinite(v));
  if (vals.length === 0) return null;

  // Include target/baseline in reference values
  const refVals = [...vals];
  if (target != null && isFinite(target)) refVals.push(target);
  if (baseline != null && isFinite(baseline)) refVals.push(baseline);

  if (vals.length < 3) {
    const mn = Math.min(...refVals);
    const mx = Math.max(...refVals);
    const m = (mx - mn) * 0.15 || 0.005;
    return { min: mn - m, max: mx + m };
  }

  // IQR method
  const sorted = [...vals].sort((a, b) => a - b);
  const q1 = sorted[Math.floor(sorted.length * 0.25)];
  const q3 = sorted[Math.floor(sorted.length * 0.75)];
  const iqr = q3 - q1 || 0.005;
  let lo = q1 - 1.5 * iqr;
  let hi = q3 + 1.5 * iqr;

  // Include target/baseline if within 2x IQR of fences
  if (target != null && isFinite(target) && target >= lo - 2 * iqr && target <= hi + 2 * iqr) {
    lo = Math.min(lo, target);
    hi = Math.max(hi, target);
  }
  if (baseline != null && isFinite(baseline) && baseline >= lo - 2 * iqr && baseline <= hi + 2 * iqr) {
    lo = Math.min(lo, baseline);
    hi = Math.max(hi, baseline);
  }

  // Clamp to actual data range
  lo = Math.max(lo, Math.min(...vals));
  hi = Math.min(hi, Math.max(...vals));
  // But re-extend for target/baseline that are within the IQR fence
  if (target != null && isFinite(target) && target >= q1 - 1.5 * iqr && target <= q3 + 1.5 * iqr) {
    lo = Math.min(lo, target);
    hi = Math.max(hi, target);
  }
  if (baseline != null && isFinite(baseline) && baseline >= q1 - 1.5 * iqr && baseline <= q3 + 1.5 * iqr) {
    lo = Math.min(lo, baseline);
    hi = Math.max(hi, baseline);
  }

  const margin = (hi - lo) * 0.12 || 0.005;
  return { min: lo - margin, max: hi + margin };
}

function updateZoomToggle() {
  const btn = document.getElementById('chartZoomToggle');
  if (!btn) return;
  if (zoomState.mode === 'auto') {
    btn.textContent = 'Auto-focus';
    btn.classList.add('active');
  } else {
    btn.textContent = 'Show all';
    btn.classList.remove('active');
  }
}

function buildChartData(solutions, progression, higherIsBetter, sentinel, decimals) {
  // Collect all valid solution scores as scatter points
  const allPoints = [];
  const genMap = {};  // gen -> [scores]

  if (solutions && solutions.length > 0) {
    solutions.forEach(s => {
      if (s.score == null || s.is_sentinel || s.score === sentinel) return;
      if (!s.is_valid) return;
      const pt = {
        gen: s.gen, score: s.score,
        agent: s.agent_type + '_' + s.instance,
        file: s.file, inProgress: s.in_progress || false,
        isGenBest: false, isRecord: false,
      };
      allPoints.push(pt);
      if (!genMap[s.gen]) genMap[s.gen] = [];
      genMap[s.gen].push(pt);
    });
  }

  // If no solution-level data, fall back to progression for gen bests
  if (allPoints.length === 0 && progression && progression.length > 0) {
    progression.forEach(p => {
      if (p.best_fitness == null) return;
      const pt = {
        gen: p.gen, score: p.best_fitness,
        agent: '?', file: '?', inProgress: false,
        isGenBest: true, isRecord: false,
      };
      allPoints.push(pt);
      genMap[p.gen] = [pt];
    });
  }

  // Determine gen bests
  const genBests = [];
  const isBetter = higherIsBetter
    ? (a, b) => a > b
    : (a, b) => a < b;

  for (const gen of Object.keys(genMap).map(Number).sort((a, b) => a - b)) {
    const pts = genMap[gen];
    let best = pts[0];
    for (let i = 1; i < pts.length; i++) {
      if (isBetter(pts[i].score, best.score)) best = pts[i];
    }
    best.isGenBest = true;
    genBests.push(best);
  }

  // Compute running best (monotonically improving) and mark records
  // Only show record star if improvement is visible at display precision (≥1 least-significant digit)
  const minDelta = Math.pow(10, -(decimals || 4));
  const runningBest = [];
  let currentBest = null;
  for (const gb of genBests) {
    if (currentBest == null || isBetter(gb.score, currentBest.score)) {
      const isSignificant = currentBest == null || Math.abs(gb.score - currentBest.score) >= minDelta;
      currentBest = gb;
      if (isSignificant) gb.isRecord = true;
    }
    runningBest.push({ gen: gb.gen, score: currentBest.score });
  }

  return { allPoints, genBests, runningBest, records: genBests.filter(p => p.isRecord) };
}

function drawChart(chartData, target, higherIsBetter, baseline, decimals) {
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

  const pad = { top: 28, right: 20, bottom: 32, left: 66 };
  const chartW = W - pad.left - pad.right;
  const chartH = H - pad.top - pad.bottom;

  const { allPoints, genBests, runningBest, records } = chartData;

  if (allPoints.length === 0 && baseline == null) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('No data yet \u2014 waiting for first generation', W / 2, H / 2);
    chartPoints = [];
    chartState = null;
    return;
  }

  // ---- Axes range ----
  const allScores = allPoints.map(p => p.score);
  const fullValues = [
    ...allScores,
    ...(target != null ? [target] : []),
    ...(baseline != null ? [baseline] : []),
  ].filter(v => v != null && isFinite(v));

  const fullMin = Math.min(...fullValues) - (Math.max(...fullValues) - Math.min(...fullValues)) * 0.12 || -0.01;
  const fullMax = Math.max(...fullValues) + (Math.max(...fullValues) - Math.min(...fullValues)) * 0.12 || 0.01;

  let minS, maxS;
  if (zoomState.yMin != null && zoomState.yMax != null) {
    minS = zoomState.yMin;
    maxS = zoomState.yMax;
  } else if (zoomState.mode === 'auto' && allScores.length >= 1) {
    const autoRange = computeAutoRange(allScores, target, baseline);
    if (autoRange) { minS = autoRange.min; maxS = autoRange.max; }
    else { minS = fullMin; maxS = fullMax; }
  } else {
    minS = fullMin; maxS = fullMax;
  }

  const maxGen = Math.max(...allPoints.map(p => p.gen), 5);
  const xPad = 0.5;  // half-unit margin so first/last gen aren't at the edge

  function xPos(gen) { return pad.left + ((gen + xPad) / (maxGen + 2 * xPad)) * chartW; }
  function yPos(score) { return pad.top + chartH - ((score - minS) / (maxS - minS)) * chartH; }

  chartState = { pad, W, H, chartW, chartH, minS, maxS, fullMin, fullMax, maxGen, dec, xPos, yPos, higherIsBetter };

  // ---- Layer 0: Grid ----
  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 1;
  const gridLines = 6;
  for (let i = 0; i <= gridLines; i++) {
    const yy = pad.top + (i / gridLines) * chartH;
    ctx.beginPath();
    ctx.moveTo(pad.left, yy);
    ctx.lineTo(W - pad.right, yy);
    ctx.stroke();

    const label = (maxS - (i / gridLines) * (maxS - minS)).toFixed(dec);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(label, pad.left - 8, yy + 3);
  }

  // X axis
  ctx.textAlign = 'center';
  ctx.fillStyle = '#475569';
  ctx.font = '10px JetBrains Mono, monospace';
  const xStep = Math.max(1, Math.floor(maxGen / 10));
  for (let g = 0; g <= maxGen; g += xStep) {
    ctx.fillText('G' + g, xPos(g), H - 8);
  }

  // ---- Layer 1: Baseline line ----
  if (baseline != null) {
    const by = yPos(baseline);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, by);
    ctx.lineTo(W - pad.right, by);
    ctx.stroke();
    ctx.setLineDash([]);
    // Label — position on right side to avoid overlap with direction arrow
    ctx.fillStyle = 'rgba(148, 163, 184, 0.8)';
    ctx.font = '9px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText('BASELINE ' + baseline.toFixed(dec), W - pad.right - 5, by - 5);
  }

  // ---- Layer 2: Target line ----
  if (target != null) {
    const ty = yPos(target);
    ctx.strokeStyle = 'rgba(5, 150, 105, 0.35)';
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, ty);
    ctx.lineTo(W - pad.right, ty);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(5, 150, 105, 0.6)';
    ctx.font = '9px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText('TARGET ' + target.toFixed(dec), pad.left + 5, ty - 5);
  }

  // Direction indicator — top-right corner (no overlap)
  ctx.fillStyle = '#94a3b8';
  ctx.font = '9px JetBrains Mono, monospace';
  ctx.textAlign = 'right';
  ctx.fillText(higherIsBetter ? '\u2191 better' : '\u2193 better', W - pad.right - 5, pad.top + 10);

  // ---- Clip to chart area for data layers ----
  ctx.save();
  ctx.beginPath();
  ctx.rect(pad.left - 2, pad.top - 2, chartW + 4, chartH + 4);
  ctx.clip();

  // ---- Layer 3: Scatter — all solutions as small dots ----
  allPoints.forEach(pt => {
    pt.px = xPos(pt.gen);
    pt.py = yPos(pt.score);
  });

  allPoints.forEach(pt => {
    if (pt.isGenBest || pt.isRecord) return; // drawn later
    ctx.fillStyle = pt.inProgress ? 'rgba(37, 99, 235, 0.25)' : 'rgba(148, 163, 184, 0.35)';
    ctx.beginPath();
    ctx.arc(pt.px, pt.py, 2.5, 0, Math.PI * 2);
    ctx.fill();
  });

  // ---- Layer 4: Best-so-far fill + line (connecting records) ----
  if (records.length > 0) {
    // Gradient fill under the line through records
    const betterY = higherIsBetter ? yPos(maxS) : yPos(minS);
    const worseY = higherIsBetter ? yPos(minS) : yPos(maxS);
    const grad = ctx.createLinearGradient(0, betterY, 0, worseY);
    grad.addColorStop(0, 'rgba(5, 150, 105, 0.12)');
    grad.addColorStop(1, 'rgba(5, 150, 105, 0)');

    // Shaded area under running-best line
    if (runningBest.length > 1) {
      ctx.fillStyle = grad;
      ctx.beginPath();
      const baseY = higherIsBetter ? yPos(minS) : yPos(maxS);
      ctx.moveTo(xPos(runningBest[0].gen), baseY);
      for (const rb of runningBest) {
        ctx.lineTo(xPos(rb.gen), yPos(rb.score));
      }
      const last = runningBest[runningBest.length - 1];
      ctx.lineTo(xPos(last.gen), baseY);
      ctx.closePath();
      ctx.fill();
    }

    // Running-best line: diagonal when improving, horizontal when flat
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    runningBest.forEach((rb, i) => {
      const rx = xPos(rb.gen);
      const ry = yPos(rb.score);
      if (i === 0) ctx.moveTo(rx, ry);
      else ctx.lineTo(rx, ry);
    });
    ctx.stroke();
  }

  // ---- Layer 5: Gen-best dots (medium, blue) ----
  genBests.forEach(pt => {
    if (pt.isRecord) return; // drawn as star
    ctx.fillStyle = '#2563eb';
    ctx.beginPath();
    ctx.arc(pt.px, pt.py, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(pt.px, pt.py, 1.5, 0, Math.PI * 2);
    ctx.fill();
  });

  // ---- Layer 6: Record stars (new best ever) ----
  records.forEach(pt => {
    drawStar(ctx, pt.px, pt.py, 5, 8, 4, '#059669');
    // White center
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(pt.px, pt.py, 2, 0, Math.PI * 2);
    ctx.fill();
  });

  // ---- Layer 7: Selected point highlight ----
  if (selectedPoint) {
    const sp = selectedPoint;
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(sp.px, sp.py, 10, 0, Math.PI * 2);
    ctx.stroke();
  }

  // ---- Layer 8: Frontier annotations (when toggled on) ----
  if (showFrontier && frontierData && frontierData.length > 0) {
    const annotWidth = 180;
    const annotHeight = 56;
    const stemLen = 24;

    frontierData.forEach((f, i) => {
      const px = xPos(f.gen);
      const py = yPos(f.score);

      // Alternate above/below to avoid overlap
      const above = (i % 2 === 0);
      const annotY = above ? py - stemLen - annotHeight : py + stemLen;
      const annotX = Math.max(pad.left, Math.min(px - annotWidth / 2, W - pad.right - annotWidth));

      // Stem line (dashed)
      ctx.strokeStyle = 'rgba(5, 150, 105, 0.4)';
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(px, above ? annotY + annotHeight : annotY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Annotation box
      ctx.fillStyle = 'rgba(245, 247, 250, 0.92)';
      ctx.beginPath();
      ctx.roundRect(annotX, annotY, annotWidth, annotHeight, 4);
      ctx.fill();
      ctx.strokeStyle = 'rgba(5, 150, 105, 0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(annotX, annotY, annotWidth, annotHeight, 4);
      ctx.stroke();

      // Text: agent + gen
      ctx.fillStyle = '#1e293b';
      ctx.font = 'bold 9px JetBrains Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText('G' + f.gen + ' ' + (f.agent || ''), annotX + 6, annotY + 13);

      // Score + delta
      ctx.fillStyle = '#059669';
      ctx.font = '9px JetBrains Mono, monospace';
      const delta = f.delta_pct != null ? ' (' + (f.delta_pct > 0 ? '+' : '') + f.delta_pct.toFixed(1) + '%)' : '';
      ctx.fillText(f.score.toFixed(dec) + delta, annotX + 6, annotY + 25);

      // Central ideas (truncated)
      ctx.fillStyle = '#64748b';
      ctx.font = '8px JetBrains Mono, monospace';
      const ideasText = (f.central_ideas || []).slice(0, 2).join(', ');
      const truncatedIdeas = ideasText.length > 28 ? ideasText.slice(0, 25) + '...' : ideasText;
      ctx.fillText(truncatedIdeas, annotX + 6, annotY + 37);

      // Label
      if (f.label) {
        ctx.fillStyle = '#475569';
        ctx.font = 'italic 8px JetBrains Mono, monospace';
        const labelTrunc = f.label.length > 28 ? f.label.slice(0, 25) + '...' : f.label;
        ctx.fillText(labelTrunc, annotX + 6, annotY + 49);
      }
    });
  }

  // ---- End clip ----
  ctx.restore();

  // ---- Outlier indicators ----
  const aboveCount = allPoints.filter(p => p.py < pad.top).length;
  const belowCount = allPoints.filter(p => p.py > pad.top + chartH).length;
  if (aboveCount > 0) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '9px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u25b2 ' + aboveCount + ' above', pad.left + chartW / 2, pad.top - 4);
  }
  if (belowCount > 0) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '9px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u25bc ' + belowCount + ' below', pad.left + chartW / 2, pad.top + chartH + 14);
  }

  // Store points for hit testing
  chartPoints = allPoints;
}

function drawStar(ctx, cx, cy, spikes, outerR, innerR, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  let rot = -Math.PI / 2;
  for (let i = 0; i < spikes; i++) {
    ctx.lineTo(cx + Math.cos(rot) * outerR, cy + Math.sin(rot) * outerR);
    rot += Math.PI / spikes;
    ctx.lineTo(cx + Math.cos(rot) * innerR, cy + Math.sin(rot) * innerR);
    rot += Math.PI / spikes;
  }
  ctx.closePath();
  ctx.fill();
}

// ---- Chart Interactivity ----
function chartHitTest(mouseX, mouseY) {
  if (!chartPoints.length) return null;
  let closest = null;
  let minDist = 20; // max pixel distance to register a hit
  for (const pt of chartPoints) {
    // Skip points outside the visible (clipped) area
    if (chartState && (pt.py < chartState.pad.top - 2 || pt.py > chartState.pad.top + chartState.chartH + 2)) continue;
    const dx = pt.px - mouseX;
    const dy = pt.py - mouseY;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d < minDist) {
      minDist = d;
      closest = pt;
    }
  }
  return closest;
}

function showChartTooltip(pt, mouseX, mouseY) {
  const tt = document.getElementById('chartTooltip');
  const container = document.getElementById('chartContainer');
  if (!tt || !container) return;

  const dec = (chartState && chartState.dec) || 4;
  const agentType = pt.agent.split('_')[0];
  const badgeClass = 'badge-' + agentType;
  let html = `<div class="tt-label">Gen ${pt.gen} &middot; ${esc(pt.agent)}</div>`;
  html += `<div class="tt-score" style="color: ${pt.isRecord ? 'var(--accent)' : 'var(--text-primary)'}">${pt.score.toFixed(dec)}</div>`;
  html += `<div style="color:var(--text-tertiary)">${esc(pt.file)}</div>`;
  if (pt.isRecord) html += `<div class="tt-record">\u2605 New record</div>`;
  else if (pt.isGenBest) html += `<div style="color:var(--blue);font-size:0.65rem">Gen best</div>`;
  if (pt.inProgress) html += `<div style="color:var(--amber);font-size:0.65rem">In progress</div>`;

  tt.innerHTML = html;
  tt.classList.add('visible');

  // Position tooltip avoiding edges
  const cRect = container.getBoundingClientRect();
  let tx = mouseX + 14;
  let ty = mouseY - 10;
  if (tx + 200 > cRect.width) tx = mouseX - 200;
  if (ty < 0) ty = mouseY + 14;
  tt.style.left = tx + 'px';
  tt.style.top = ty + 'px';
}

function hideChartTooltip() {
  const tt = document.getElementById('chartTooltip');
  if (tt) tt.classList.remove('visible');
}

// Canvas event listeners
(function initChartEvents() {
  const canvas = document.getElementById('progressionChart');
  if (!canvas) return;

  canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = chartHitTest(mx, my);
    if (hit) {
      canvas.style.cursor = 'pointer';
      showChartTooltip(hit, mx, my);
    } else {
      canvas.style.cursor = 'crosshair';
      hideChartTooltip();
    }
  });

  canvas.addEventListener('mouseleave', () => {
    hideChartTooltip();
    canvas.style.cursor = 'crosshair';
  });

  let skipNextClick = false;

  canvas.addEventListener('click', e => {
    if (skipNextClick) { skipNextClick = false; return; }
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = chartHitTest(mx, my);
    if (hit) {
      selectedPoint = hit;
      redrawChart();
    } else {
      selectedPoint = null;
      redrawChart();
    }
  });

  // Wheel zoom — centered on cursor Y position
  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    if (!chartState) return;

    const rect = canvas.getBoundingClientRect();
    const my = e.clientY - rect.top;
    const { pad: p, chartH: ch, minS: curMin, maxS: curMax, fullMin: fMin, fullMax: fMax } = chartState;

    // Convert mouse Y to score
    const frac = 1 - (my - p.top) / ch;
    const centerScore = curMin + frac * (curMax - curMin);

    // Zoom factor: 10% per tick
    const factor = e.deltaY > 0 ? 1.1 : 0.9;
    let newMin = centerScore - (centerScore - curMin) * factor;
    let newMax = centerScore + (curMax - centerScore) * factor;

    // Clamp to full data range
    if (newMin < fMin) newMin = fMin;
    if (newMax > fMax) newMax = fMax;
    if (newMax - newMin < 0.0001) return;

    zoomState.yMin = newMin;
    zoomState.yMax = newMax;
    zoomState.mode = 'manual';
    updateZoomToggle();
    redrawChart();
  }, { passive: false });

  // Double-click to reset zoom
  canvas.addEventListener('dblclick', () => {
    skipNextClick = true;
    zoomState = { mode: 'auto', yMin: null, yMax: null };
    updateZoomToggle();
    redrawChart();
  });

  // Toggle button
  const zoomBtn = document.getElementById('chartZoomToggle');
  if (zoomBtn) {
    zoomBtn.addEventListener('click', () => {
      if (zoomState.mode === 'auto') {
        zoomState = { mode: 'full', yMin: null, yMax: null };
      } else {
        zoomState = { mode: 'auto', yMin: null, yMax: null };
      }
      updateZoomToggle();
      redrawChart();
    });
  }

  // Frontier toggle button
  const frontierBtn = document.getElementById('chartFrontierToggle');
  if (frontierBtn) {
    frontierBtn.addEventListener('click', () => {
      showFrontier = !showFrontier;
      frontierBtn.classList.toggle('active', showFrontier);
      if (showFrontier && !frontierData) {
        apiFetch('/api/frontier').then(data => {
          if (data && data.frontier) {
            frontierData = data.frontier;
          }
          redrawChart();
        });
      } else {
        redrawChart();
      }
    });
  }
})();

// Centralized chart redraw — call after data changes or window resize
function redrawChart() {
  if (!overviewData) return;
  // Reset auto-range on data refresh so it recomputes with new data
  if (zoomState.mode === 'auto') {
    zoomState.yMin = null;
    zoomState.yMax = null;
  }
  const c = overviewData.config;
  const sv = c.sentinel_value;
  const hib = c.higher_is_better;
  const ns = v => v != null && v !== sv;

  // Baseline
  const initScores = (overviewData.initial_scores || []).filter(x => ns(x.score)).map(x => x.score);
  let bl = initScores.length > 0 ? (hib ? Math.max(...initScores) : Math.min(...initScores)) : null;
  if (bl == null && c.baseline_score != null) bl = c.baseline_score;

  // Progression fallback (if no solutions data yet)
  let prog = overviewData.progression
    ? overviewData.progression.filter(p => ns(p.best_fitness))
    : [];
  if (prog.length === 0 && overviewData.generations.length > 0) {
    prog = overviewData.generations.filter(g => ns(g.best_score)).map(g => ({ gen: g.gen, best_fitness: g.best_score }));
  }
  // Append in-progress generations
  if (prog.length > 0 && overviewData.generations.length > 0) {
    const progGens = new Set(prog.map(p => p.gen));
    overviewData.generations.forEach(g => {
      if (ns(g.best_score) && !progGens.has(g.gen)) {
        prog.push({ gen: g.gen, best_fitness: g.best_score });
      }
    });
    prog.sort((a, b) => a.gen - b.gen);
  }

  // Inject initial programs as gen 0 points
  const initPts = (overviewData.initial_scores || [])
    .filter(x => ns(x.score) && x.is_valid)
    .map(x => ({ gen: 0, score: x.score, agent_type: 'initial', instance: '0',
                  file: x.file, is_valid: true, is_sentinel: false }));
  const allSols = initPts.concat(solutionsData || []);

  const dec = c.decimals || 4;
  const chartData = buildChartData(allSols, prog, hib, sv, dec);
  drawChart(chartData, c.target_score, hib, bl, dec);
}

// Chart redraws on data refresh, not on window resize

// ----- Solutions -----
async function loadSolutions() {
  solutionsData = await apiFetch('/api/solutions');
  // Set correct initial sort direction based on fitness direction
  if (overviewData && overviewData.config && solSort.key === 'score') {
    solSort.dir = overviewData.config.higher_is_better ? -1 : 1;
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

  // Sort — sentinels and nulls always go to the bottom
  const sv = (overviewData && overviewData.config) ? overviewData.config.sentinel_value : null;
  filtered.sort((a, b) => {
    let av = a[solSort.key], bv = b[solSort.key];
    // Push sentinel/null to bottom regardless of direction
    const aBottom = av == null || (solSort.key === 'score' && (a.is_sentinel || av === sv));
    const bBottom = bv == null || (solSort.key === 'score' && (b.is_sentinel || bv === sv));
    if (aBottom && bBottom) return 0;
    if (aBottom) return 1;
    if (bBottom) return -1;
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
    const isSentinel = s.is_sentinel || (sv != null && s.score === sv);
    const scoreClass = s.score == null ? 'score-none' : isSentinel ? 'score-none' : '';
    const dec = (overviewData && overviewData.config) ? overviewData.config.decimals || 4 : 4;
    const scoreText = isSentinel ? 'ERR' : (s.score != null ? s.score.toFixed(dec) : '--');
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
    else {
      solSort.key = key;
      if (key === 'score') {
        // Best-first: descending for higher-is-better, ascending for lower-is-better
        const hib = overviewData && overviewData.config ? overviewData.config.higher_is_better : true;
        solSort.dir = hib ? -1 : 1;
      } else {
        solSort.dir = 1;
      }
    }

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
function renderFeedback(data) {
  const section = document.getElementById('feedbackSection');
  const empty = document.getElementById('feedbackEmpty');
  if (!section) return;

  if (!data || (!data.recommendations && data.analyses.length === 0 && data.consistency_reviews.length === 0)) {
    section.innerHTML = '';
    section.appendChild(empty);
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';
  let html = '<div class="feedback-cards">';

  // Current recommendations
  if (data.recommendations) {
    html += `
      <div class="feedback-card feedback-recs">
        <div class="feedback-card-header" onclick="this.parentElement.classList.toggle('open')">
          <span class="feedback-toggle">&#9654;</span>
          <span class="feedback-badge recs">Recommendations</span>
          <span class="feedback-label">Current system critic recommendations</span>
        </div>
        <div class="feedback-card-body"><pre class="feedback-pre">${esc(data.recommendations)}</pre></div>
      </div>`;
  }

  // Analyses (newest first)
  data.analyses.forEach(a => {
    const ipBadge = a.in_progress ? '<span class="live-agent-status-label" style="margin-left:6px;font-size:0.58rem;color:var(--amber)">IN PROGRESS</span>' : '';
    html += `
      <div class="feedback-card feedback-analysis">
        <div class="feedback-card-header" onclick="this.parentElement.classList.toggle('open')">
          <span class="feedback-toggle">&#9654;</span>
          <span class="feedback-badge analysis">Critic Analysis</span>
          <span class="report-gen-badge">Gen ${a.gen}</span>${ipBadge}
        </div>
        <div class="feedback-card-body"><pre class="feedback-pre">${esc(a.content)}</pre></div>
      </div>`;
  });

  // Consistency reviews
  data.consistency_reviews.forEach(r => {
    html += `
      <div class="feedback-card feedback-consistency">
        <div class="feedback-card-header" onclick="this.parentElement.classList.toggle('open')">
          <span class="feedback-toggle">&#9654;</span>
          <span class="feedback-badge consistency">Consistency Review</span>
          <span class="report-gen-badge">Gen ${r.gen}</span>
        </div>
        <div class="feedback-card-body"><pre class="feedback-pre">${esc(r.content)}</pre></div>
      </div>`;
  });

  html += '</div>';
  section.innerHTML = html;
}

async function loadReports() {
  // Load feedback (critic/consistency) in parallel with reports
  apiFetch('/api/feedback').then(renderFeedback);

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

  // Render run_state agents + errors from cached overview
  const rs = overviewData?.run_state;
  renderRunStateAgents(rs?.agents);
  renderPipelineErrors(rs?.errors);
  rescheduleRefresh(loadActiveAgents, 'agent');

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
refreshTimer = setInterval(loadOverview, getRefreshInterval());

// Manual refresh button
document.getElementById('refreshBtn')?.addEventListener('click', () => {
  const activeTab = document.querySelector('.nav-btn.active')?.dataset.tab;
  if (activeTab === 'overview') loadOverview();
  else if (activeTab === 'solutions') loadSolutions();
  else if (activeTab === 'knowledge') loadKnowledge();
  else if (activeTab === 'reports') loadReports();
  else if (activeTab === 'architecture') loadFiles();
  else if (activeTab === 'pipeline') { loadOverview(); loadActiveAgents(); }
  else loadOverview();
});
