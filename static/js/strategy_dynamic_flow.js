/**
 * Stratejik Planlama Akışı - Dinamik Grafik
 * Config: window.STRATEGY_FLOW_CONFIG = { apiUrl, tenantId }
 * vis-network CDN'den yüklenmeli; SweetAlert2 bildirimler için kullanılır.
 */
(function () {
  'use strict';

  let network = null;
  let lastGraph = { nodes: [], edges: [], meta: {} };
  let refreshTimer = null;
  let searchableNodes = [];
  let searchMatches = [];
  let searchMatchIndex = 0;
  let lastFocusedNodeId = null;
  let collapsedNodes = new Set();
  let allNodes = [];
  let allEdges = [];
  let focusedNodeId = null;

  function getConfig() {
    const el = document.getElementById('strategyFlowConfig');
    if (el) {
      return {
        apiUrl: el.getAttribute('data-api-url') || '/strategy/api/strategic-planning-graph',
        tenantId: el.getAttribute('data-tenant-id') ? parseInt(el.getAttribute('data-tenant-id'), 10) : null
      };
    }
    return { apiUrl: '/strategy/api/strategic-planning-graph', tenantId: null };
  }

  function buildApiUrl() {
    const { apiUrl, tenantId } = getConfig();
    if (!tenantId) return apiUrl;
    const sep = apiUrl.includes('?') ? '&' : '?';
    return apiUrl + sep + 'tenant_id=' + encodeURIComponent(tenantId);
  }

  function byId(id) { return document.getElementById(id); }

  function getConnectedNodes(nodeId) {
    const connected = new Set([nodeId]);
    allEdges.forEach(e => {
      if (e.from === nodeId) connected.add(e.to);
      if (e.to === nodeId) connected.add(e.from);
    });
    return Array.from(connected);
  }

  function clearFocusMode() {
    focusedNodeId = null;
    const clearBtn = byId('clearFocusBtn');
    if (clearBtn) clearBtn.style.display = 'none';
    renderGraph(lastGraph);
  }

  function normText(s) {
    return String(s || '').replace(/\s+/g, ' ').trim().toLocaleLowerCase('tr-TR');
  }

  function plainLabel(node) {
    const label = String(node?.label || '').replace(/\n/g, ' ');
    return label.replace(/\s*\(\s*\d+\s*%\s*\)\s*$/g, '').trim();
  }

  function groupName(group) {
    switch (group) {
      case 'main_strategy': return 'Ana';
      case 'sub_strategy': return 'Alt';
      case 'process': return 'Süreç';
      case 'kpi': return 'PG';
      default: return group || '';
    }
  }

  function focusNode(nodeId) {
    if (!network || !nodeId) return;
    lastFocusedNodeId = nodeId;
    network.selectNodes([nodeId]);
    network.focus(nodeId, {
      scale: 1.15,
      animation: { duration: 500, easingFunction: 'easeInOutQuad' }
    });
  }

  function renderSearchResults(matches) {
    const resultsEl = byId('searchResults');
    const metaEl = byId('searchMeta');
    if (!resultsEl || !metaEl) return;

    if (!matches || matches.length === 0) {
      resultsEl.style.display = 'none';
      metaEl.innerHTML = byId('nodeSearch')?.value ? '<i class="fas fa-info-circle me-2"></i>Sonuç bulunamadı.' : '';
      return;
    }

    metaEl.innerHTML = `<i class="fas fa-check-circle me-2" style="color: #10b981;"></i>${matches.length} sonuç bulundu`;
    resultsEl.innerHTML = '';
    resultsEl.style.display = 'block';

    matches.slice(0, 12).forEach((n, idx) => {
      const a = document.createElement('button');
      a.type = 'button';
      a.className = 'list-group-item list-group-item-action search-results-item py-2';
      a.dataset.nodeId = n.id;
      a.innerHTML = `<div class="d-flex justify-content-between align-items-center gap-2">
          <div class="text-truncate" style="font-weight: 500;">${plainLabel(n) || String(n.id)}</div>
          <span class="badge" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); color: #667eea; border: 1px solid rgba(102, 126, 234, 0.3);">${groupName(n.group)}</span>
        </div>`;
      a.addEventListener('click', () => focusNode(n.id));
      resultsEl.appendChild(a);
      if (idx === 0) a.classList.add('active');
    });
  }

  function runSearch() {
    const q = normText(byId('nodeSearch')?.value);
    if (!q) {
      searchMatches = [];
      searchMatchIndex = 0;
      renderSearchResults([]);
      return;
    }

    const matches = (searchableNodes || []).filter(n => {
      const hay = normText(`${plainLabel(n)} ${n.title || ''}`);
      return hay.includes(q);
    });

    matches.sort((a, b) => {
      const aL = normText(plainLabel(a));
      const bL = normText(plainLabel(b));
      const aStarts = aL.startsWith(q) ? 0 : 1;
      const bStarts = bL.startsWith(q) ? 0 : 1;
      if (aStarts !== bStarts) return aStarts - bStarts;
      return aL.localeCompare(bL, 'tr');
    });

    searchMatches = matches;
    searchMatchIndex = 0;
    renderSearchResults(searchMatches);
  }

  function focusNextMatch() {
    if (!searchMatches || searchMatches.length === 0) return;
    const n = searchMatches[searchMatchIndex % searchMatches.length];
    searchMatchIndex = (searchMatchIndex + 1) % searchMatches.length;
    focusNode(n.id);
  }

  function getChildNodes(nodeId) {
    return allEdges.filter(e => e.from === nodeId).map(e => e.to);
  }

  function getAllDescendants(nodeId, visited = new Set()) {
    if (visited.has(nodeId)) return [];
    visited.add(nodeId);
    const children = getChildNodes(nodeId);
    const descendants = [...children];
    children.forEach(childId => {
      descendants.push(...getAllDescendants(childId, visited));
    });
    return descendants;
  }

  function applyFilters(graph) {
    const showKpis = byId('showKpis')?.checked;
    const showDerived = byId('showDerived')?.checked;

    allNodes = graph.nodes || [];
    allEdges = graph.edges || [];

    let nodes = allNodes.filter(n => {
      if (!showKpis && n.group === 'kpi') return false;
      return true;
    });

    if (collapsedNodes.size > 0) {
      const hiddenNodes = new Set();
      collapsedNodes.forEach(collapsedId => {
        getAllDescendants(collapsedId).forEach(d => hiddenNodes.add(d));
      });
      nodes = nodes.filter(n => !hiddenNodes.has(n.id));
    }

    if (focusedNodeId) {
      const connectedNodes = getConnectedNodes(focusedNodeId);
      nodes = nodes.filter(n => connectedNodes.includes(n.id));
    }

    const nodeIdSet = new Set(nodes.map(n => n.id));

    const edges = allEdges.filter(e => {
      if (!showDerived && e.dashes === true) {
        const from = String(e.from || '');
        const to = String(e.to || '');
        if (from.startsWith('proj_') && to.startsWith('sub_')) return false;
      }
      return nodeIdSet.has(e.from) && nodeIdSet.has(e.to);
    });

    return { nodes, edges, meta: graph.meta || {} };
  }

  function renderGraph(graph) {
    const container = byId('spGraph');
    if (!container) return;

    const filtered = applyFilters(graph);
    searchableNodes = filtered.nodes || [];

    const data = {
      nodes: new vis.DataSet(filtered.nodes),
      edges: new vis.DataSet(filtered.edges)
    };

    const isCompact = byId('compactView')?.checked;
    const levelSep = isCompact ? 180 : 320;
    const nodeSpace = isCompact ? 120 : 220;
    const treeSpace = isCompact ? 150 : 300;

    const options = {
      layout: {
        hierarchical: {
          enabled: true,
          direction: 'UD',
          levelSeparation: levelSep,
          nodeSpacing: nodeSpace,
          treeSpacing: treeSpace,
          sortMethod: 'directed',
          shakeTowards: 'roots'
        }
      },
      physics: { enabled: false },
      interaction: {
        hover: true,
        tooltipDelay: 80,
        zoomView: true,
        dragView: true,
        multiselect: false
      },
      nodes: {
        font: { size: 15, face: 'Segoe UI', bold: { color: '#1f2937' }, multi: 'html' },
        borderWidth: 3,
        margin: 16,
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.2)',
          size: 10,
          x: 2,
          y: 5
        },
        widthConstraint: { maximum: 280 }
      },
      edges: {
        font: { size: 12, align: 'middle', strokeWidth: 0, background: 'rgba(255,255,255,0.8)' },
        smooth: {
          type: 'cubicBezier',
          forceDirection: 'vertical',
          roundness: 0.5
        },
        arrows: { to: { enabled: true, scaleFactor: 1.0 } }
      }
    };

    if (!network) {
      network = new vis.Network(container, data, options);

      network.on('click', function (params) {
        if (params.nodes && params.nodes.length === 1) {
          focusedNodeId = params.nodes[0];
          const clearBtn = byId('clearFocusBtn');
          if (clearBtn) clearBtn.style.display = 'inline-block';
          renderGraph(lastGraph);
        } else if (params.nodes.length === 0 && params.edges.length === 0) {
          if (focusedNodeId) clearFocusMode();
        }
      });

      network.on('doubleClick', function (params) {
        const nodeId = params.nodes && params.nodes[0];
        if (!nodeId) return;

        if (focusedNodeId) {
          const node = allNodes.find(n => n.id === nodeId);
          if (node && node.url) window.location.href = node.url;
          return;
        }

        const hasChildren = getChildNodes(nodeId).length > 0;
        if (!hasChildren) {
          const node = allNodes.find(n => n.id === nodeId);
          if (node && node.url) window.location.href = node.url;
          return;
        }

        if (collapsedNodes.has(nodeId)) {
          collapsedNodes.delete(nodeId);
        } else {
          collapsedNodes.add(nodeId);
        }
        renderGraph(lastGraph);
      });

      network.on('hoverNode', function () { container.style.cursor = 'pointer'; });
      network.on('blurNode', function () { container.style.cursor = 'default'; });
    } else {
      network.setData(data);
      network.setOptions(options);
    }

    runSearch();
    if (lastFocusedNodeId && searchableNodes.some(n => n.id === lastFocusedNodeId)) {
      focusNode(lastFocusedNodeId);
    }

    const meta = filtered.meta || {};
    const statMain = byId('statMainStrategies');
    const statSub = byId('statSubStrategies');
    const statProc = byId('statProcesses');
    const statKpi = byId('statKpis');
    if (statMain) statMain.textContent = meta.main_strategies ?? 0;
    if (statSub) statSub.textContent = meta.sub_strategies ?? 0;
    if (statProc) statProc.textContent = meta.processes ?? 0;
    if (statKpi) statKpi.textContent = meta.kpis ?? 0;

    const loadingOverlay = byId('loadingOverlay');
    if (loadingOverlay) loadingOverlay.style.display = 'none';
  }

  async function fetchGraph() {
    const loadingOverlay = byId('loadingOverlay');
    if (loadingOverlay) loadingOverlay.style.display = 'flex';

    const url = buildApiUrl();
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    const data = await res.json();

    if (!data || !data.success) {
      if (loadingOverlay) loadingOverlay.style.display = 'none';
      const msg = (data && data.message) ? data.message : 'Grafik yüklenemedi';
      if (typeof Swal !== 'undefined') {
        Swal.fire({ icon: 'error', title: 'Hata', text: msg });
      } else {
        throw new Error(msg);
      }
      return;
    }

    lastGraph = data;
    renderGraph(lastGraph);
  }

  function scheduleAutoRefresh() {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
    if (byId('autoRefresh')?.checked) {
      refreshTimer = setInterval(() => fetchGraph().catch(err => console.error(err)), 30000);
    }
  }

  function showError(msg) {
    if (typeof Swal !== 'undefined') {
      Swal.fire({ icon: 'error', title: 'Hata', text: msg || 'Beklenmeyen bir hata oluştu.' });
    } else {
      console.error(msg);
    }
  }

  function init() {
    if (typeof vis === 'undefined') {
      const msg = 'Grafik kütüphanesi (vis-network) yüklenemedi. CDN engelleniyor olabilir.';
      if (typeof Swal !== 'undefined') {
        Swal.fire({ icon: 'warning', title: 'Uyarı', text: msg });
      } else {
        console.warn(msg);
      }
      return;
    }

    const searchInput = byId('nodeSearch');
    const clearBtn = byId('clearSearch');

    searchInput?.addEventListener('input', () => runSearch());
    searchInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        focusNextMatch();
      }
      if (e.key === 'Escape') {
        if (searchInput) searchInput.value = '';
        runSearch();
      }
    });

    clearBtn?.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      runSearch();
      searchInput?.focus();
    });

    byId('refreshBtn')?.addEventListener('click', () => {
      const btn = byId('refreshBtn');
      const icon = btn?.querySelector('i');
      if (icon) icon.style.animation = 'spin 0.8s linear infinite';
      fetchGraph()
        .catch(err => showError(err.message || String(err)))
        .finally(() => {
          if (icon) icon.style.animation = '';
        });
    });

    ['autoRefresh', 'showKpis', 'showDerived'].forEach(id => {
      byId(id)?.addEventListener('change', () => {
        scheduleAutoRefresh();
        renderGraph(lastGraph);
      });
    });

    byId('expandAllBtn')?.addEventListener('click', () => {
      collapsedNodes.clear();
      renderGraph(lastGraph);
    });

    byId('collapseAllBtn')?.addEventListener('click', () => {
      const mainStrategies = allNodes.filter(n => n.group === 'main_strategy');
      collapsedNodes.clear();
      mainStrategies.forEach(n => collapsedNodes.add(n.id));
      renderGraph(lastGraph);
    });

    byId('zoomInBtn')?.addEventListener('click', () => {
      if (network) {
        const scale = network.getScale();
        network.moveTo({ scale: scale * 1.3, animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
      }
    });

    byId('zoomOutBtn')?.addEventListener('click', () => {
      if (network) {
        const scale = network.getScale();
        network.moveTo({ scale: scale * 0.7, animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
      }
    });

    byId('fitBtn')?.addEventListener('click', () => {
      if (network) network.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
    });

    byId('compactView')?.addEventListener('change', () => renderGraph(lastGraph));

    byId('clearFocusBtn')?.addEventListener('click', () => clearFocusMode());

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && focusedNodeId) clearFocusMode();
    });

    fetchGraph().catch(err => showError(err.message || String(err)));
    scheduleAutoRefresh();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
