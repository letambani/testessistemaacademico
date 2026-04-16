// scripts.js (index-1.html — módulo de análises)
// requer Plotly e Bootstrap bundle pré-carregados.

// util
const qs = id => document.getElementById(id);
const showError = msg => alert(msg);

/** Rola a página até a área de resultados (index-1 / index com #secaoResultado). */
function scrollToSecaoResultado() {
  const el = document.getElementById('secaoResultado');
  if (!el) return;
  requestAnimationFrame(() => {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

// recarregar arquivos
qs('refreshFilesBtn')?.addEventListener('click', () => location.reload());

// UPLOAD CSV
qs('uploadBtnModal')?.addEventListener('click', () => {
  const input = qs('csvFile');
  const file = input.files[0];
  if (!file) { showError('Selecione um CSV.'); return; }

  const fd = new FormData();
  fd.append('file', file);

  fetch('/upload', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(js => {
      if (js.success) {
        alert('Upload efetuado com sucesso.');
        location.reload();
      } else {
        showError(js.error || 'Erro no upload.');
      }
    })
    .catch(() => showError('Erro no upload.'));
});

// Carrega lista de arquivos ao abrir o modal
document.getElementById("manageFilesModal")
  .addEventListener("shown.bs.modal", loadFilesList);


// Buscar arquivos em tempo real
document.getElementById("searchFiles").addEventListener("keyup", () => {
  const term = document.getElementById("searchFiles").value.toLowerCase();
  const items = document.querySelectorAll("#filesList li");

  items.forEach(li => {
    li.style.display = li.textContent.toLowerCase().includes(term) ? "block" : "none";
  });
});


// Função para carregar arquivos
function loadFilesList() {
  fetch("/list_files")
    .then(r => r.json())
    .then(data => {
      const list = document.getElementById("filesList");
      list.innerHTML = "";

      if (data.files.length === 0) {
        list.innerHTML = `<li class="list-group-item text-center text-muted">Nenhum arquivo encontrado.</li>`;
        return;
      }

      data.files.forEach(file => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";

        li.innerHTML = `
                    <span>${file}</span>
                    <button class="btn btn-danger btn-sm" onclick="deleteFile('${file}')">Excluir</button>
                `;
        list.appendChild(li);
      });
    });
}


// Excluir arquivo
function deleteFile(filename) {
  if (!confirm(`Tem certeza que deseja excluir o arquivo:\n\n${filename}?`)) {
    return;
  }

  fetch("/delete_file", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename })
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        loadFilesList(); // Recarrega lista
        alert("Arquivo removido com sucesso.");
      } else {
        alert("Erro ao remover: " + data.error);
      }
    });
}

// Quando muda a origem dos dados
qs('dataOrigin')?.addEventListener('change', () => {
  const origin = qs('dataOrigin').value;
  if (origin === 'db') {
    qs('csvSelectors').style.display = 'none';
    const compareCardBody = qs('arquivoCompare').closest('.card-body');
    if (compareCardBody) {
        const note = compareCardBody.querySelector('p.small.text-muted.mb-2');
        if (note) note.style.display = 'none';
    }
    qs('arquivoCompare').style.display = 'none';
    qs('btnGerarComparar').style.display = 'none';

    // Trigger columns load for DB
    loadColumns('__DB_DATA__');
  } else {
    qs('csvSelectors').style.display = 'block';
    qs('arquivoCompare').style.display = 'block';
    qs('btnGerarComparar').style.display = 'block';
    const compareCardBody = qs('arquivoCompare').closest('.card-body');
    if (compareCardBody) {
        const note = compareCardBody.querySelector('p.small.text-muted.mb-2');
        if (note) note.style.display = 'block';
    }
    qs('colunaSelect').innerHTML = '<option value="">Selecione um arquivo primeiro</option>';
    qs('colunaGroupBy').innerHTML = '<option value="">Nenhum agrupamento</option>';
    qs('filtersArea').innerHTML = '';
  }
});


// Quando muda o arquivo base: carregar colunas / filtros
qs('arquivoSelect')?.addEventListener('change', () => {
  const filename = qs('arquivoSelect').value;
  loadColumns(filename);
});

function loadColumns(filename) {
  qs('colunaSelect').innerHTML = '<option value="">Carregando colunas...</option>';
  qs('colunaGroupBy').innerHTML = '<option value="">Nenhum agrupamento</option>';
  qs('filtersArea').innerHTML = '';

  if (!filename) {
    qs('colunaSelect').innerHTML = '<option value="">Selecione um arquivo primeiro</option>';
    return;
  }

  fetch('/api/columns', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
    .then(r => r.json())
    .then(js => {
      if (js.error) { showError(js.error); return; }
      // popular selects
      qs('colunaSelect').innerHTML = '<option value="">-- escolha --</option>';
      qs('colunaGroupBy').innerHTML = '<option value="">Nenhum agrupamento</option>';
      js.columns.forEach(c => {
        const o = document.createElement('option'); o.value = c.name; o.textContent = c.name;
        qs('colunaSelect').appendChild(o);
        const o2 = o.cloneNode(true); qs('colunaGroupBy').appendChild(o2);
      });

      // criar filtros para colunas categóricas
      const filtersDiv = qs('filtersArea');
      filtersDiv.innerHTML = '<div class="small mb-2 text-muted">Filtros rápidos (marque valores)</div>';
      js.columns.forEach(c => {
        if (!c.is_numeric && c.unique_values_count <= 40) {
          const box = document.createElement('div'); box.className = 'mb-2';
          box.innerHTML = `<strong class="small">${c.name}</strong><div class="small mt-1" id="filter_${safeId(c.name)}"></div>`;
          filtersDiv.appendChild(box);
          const container = box.querySelector('div');
          c.sample_values.forEach(v => {
            const id = `cb_${safeId(c.name)}_${safeId(String(v))}`;
            const html = `<div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" id="${id}" data-col="${c.name}" value="${v}">
            <label class="form-check-label small" for="${id}">${v}</label>
          </div>`;
            container.insertAdjacentHTML('beforeend', html);
          });
        }
      });
      loadCoordinatorMeta(filename);
    })
    .catch(() => showError('Erro ao buscar colunas.'));
}

function safeId(s) { return String(s).replace(/\s+/g, '_').replace(/[^\w_-]/g, ''); }

// Gather filters
function gatherFilters() {
  const checked = document.querySelectorAll('#filtersArea input[type=checkbox]:checked');
  const filtros = {};
  checked.forEach(cb => {
    const col = cb.dataset.col;
    if (!filtros[col]) filtros[col] = [];
    filtros[col].push(cb.value);
  });
  return filtros;
}

// Render multiple graphs returned pela API
function renderGraphs(resp) {
  const container = qs('graficoContainer');
  container.innerHTML = '';
  if (!resp.graficos || resp.graficos.length === 0) {
    container.innerHTML = '<p class="text-center text-secondary">Nenhum gráfico retornado.</p>';
    scrollToSecaoResultado();
    return;
  }

  resp.graficos.forEach((g, idx) => {
    const card = document.createElement('div'); card.className = 'card';
    const header = document.createElement('div'); header.className = 'card-header d-flex justify-content-between align-items-center';
    header.style.background = '#0B3353';
    header.innerHTML = `<div><strong>${g.title}</strong></div>
      <div class="btn-group">
        <button class="btn btn-sm btn-outline-secondary" onclick="downloadPlotlyPNG('chart_${idx}')">📥 PNG</button>
      </div>`;
    card.appendChild(header);

    const body = document.createElement('div'); body.className = 'card-body';
    const plot = document.createElement('div'); plot.id = `chart_${idx}`; plot.style.height = '620px';
    body.appendChild(plot);
    card.appendChild(body);
    container.appendChild(card);

    // desenhar
    try {
      const fig = g.fig || {};
      const data = fig.data || [];
      const layout = fig.layout || {};
      // Ajusta o eixo Y para evitar cortar o valor acima da barra
      if (layout.yaxis && layout.yaxis.range) {
        const max = layout.yaxis.range[1];
        layout.yaxis.range[1] = max * 1.50;  // aumenta o topo
      } else if (layout.yaxis) {
        layout.yaxis.autorange = true;
      }

      Plotly.react(plot.id, data, layout, { responsive: true });
    } catch (e) {
      plot.innerHTML = `<pre class="text-danger">Erro ao renderizar: ${String(e)}</pre>`;
    }
  });

  qs('btnSalvarTodos')?.classList.remove('d-none');
  scrollToSecaoResultado();
}

// download helper
function downloadPlotlyPNG(divId) {
  Plotly.toImage(divId, { format: 'png', width: 1200, height: 700 })
    .then(dataUrl => {
      const a = document.createElement('a'); a.href = dataUrl; a.download = divId + '.png';
      document.body.appendChild(a); a.click(); a.remove();
    })
    .catch(() => showError('Erro ao gerar imagem'));
}

// Gerar sem comparar
qs('btnGerar')?.addEventListener('click', () => {
  coordBadgeManual();
  const origin = qs('dataOrigin').value;
  const filename = origin === 'db' ? '__DB_DATA__' : qs('arquivoSelect').value;
  const coluna = qs('colunaSelect').value;

  let tipo = qs('tipoSelect').value;     // bar/pie/line/histograma/texto
  const groupby = qs('colunaGroupBy').value || null;

  if (!filename || !coluna) {
    showError('Escolha arquivo e coluna');
    return;
  }

  const filtros = gatherFilters();

  // ----------------------------
  // SE O USUÁRIO QUER "RELATÓRIO POR EXTENSO"
  // ----------------------------
  if (tipo === "texto") {

    const payload = {
      filename,
      coluna,
      groupby,
      filtros,
      modo: "texto"
    };

    fetch('/api/grafico', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(r => r.json())
      .then(js => {
        if (js.error) { showError(js.error); return; }

        // exibe o relatório textual
        qs('graficoContainer').innerHTML = `
  <div class="card shadow-sm">
      <div class="card-header d-flex justify-content-between align-items-center" style="background:#0B3353; color:white;">
          <strong>Relatório por Extenso</strong>
          <div class="btn-group">
              <button class="btn btn-sm btn-outline-light" onclick="copyReport()">📋 Copiar</button>
              <button class="btn btn-sm btn-outline-light" onclick="downloadReportTXT()">📥 TXT</button>
          </div>
      </div>

      <div class="card-body">
          <pre id="reportText" class="p-3 bg-light border rounded"
               style="white-space: pre-wrap; font-size: 14px;">${js.relatorio_texto}</pre>
      </div>
  </div>
`;
        scrollToSecaoResultado();
      })
      .catch(() => showError('Erro ao gerar relatório textual.'));

    return; // <--- IMPORTANTE: parar aqui
  }

  // ----------------------------
  // MODO NORMAL: GERAR GRÁFICO
  // ----------------------------

  if (tipo === 'histogram') tipo = 'hist';

  const payload = { filename, coluna, tipo, filtros, groupby };

  fetch('/api/grafico', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(r => r.json())
    .then(js => {
      if (js.error) { showError(js.error); return; }
      renderGraphs(js);
    })
    .catch(() => showError('Erro ao chamar /api/grafico'));
});



// Gerar + comparar
qs('btnGerarComparar')?.addEventListener('click', () => {
  coordBadgeManual();
  const origin = qs('dataOrigin').value;
  if (origin === 'db') return;

  const filename = qs('arquivoSelect').value;
  const compare = qs('arquivoCompare').value;
  const coluna = qs('colunaSelect').value;

  // 🔧 Ajuste do tipo de gráfico
  let tipo = qs('tipoSelect').value;
  if (tipo === 'histogram') {
    tipo = 'hist'; // <-- conversão para a API
  }

  const groupby = qs('colunaGroupBy').value || null;

  if (!filename || !coluna) { showError('Escolha arquivo base e coluna'); return; }
  if (!compare) { showError('Escolha o arquivo para comparar'); return; }
  if (compare === filename) { showError('Escolha um arquivo diferente para comparar'); return; }

  const payload = { filename, compare_with: compare, coluna, tipo, filtros: gatherFilters(), groupby };

  fetch('/api/grafico', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(r => r.json())
    .then(js => {
      if (js.error) { showError(js.error); return; }
      renderGraphs(js);
    })
    .catch(() => showError('Erro ao chamar /api/grafico'));
});


// salvar todos (opcional) - converte cada chart em png e baixa
qs('btnSalvarTodos')?.addEventListener('click', async () => {
  const charts = document.querySelectorAll('#graficoContainer [id^="chart_"]');
  for (let i = 0; i < charts.length; i++) {
    const id = charts[i].id;
    try {
      const dataUrl = await Plotly.toImage(id, { format: 'png', width: 1200, height: 700 });
      const a = document.createElement('a');
      a.href = dataUrl; a.download = `${id}.png`;
      document.body.appendChild(a); a.click(); a.remove();
    } catch (e) {
      console.warn('Erro ao salvar', id, e);
    }
  }
});

function copyReport() {
  const txt = qs("reportText").innerText;
  navigator.clipboard.writeText(txt);
  alert("Relatório copiado!");
}

function downloadReportTXT() {
  const content = qs("reportText").innerText;
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "relatorio.txt";
  a.click();
  URL.revokeObjectURL(url);
}

// ----- Análise orientada (coordenadores) -----
function coordBadgeManual() {
  const b = qs('coordModeBadge');
  if (b) { b.textContent = 'Modo manual'; b.className = 'badge rounded-pill bg-secondary'; }
}
function coordBadgeOriented() {
  const b = qs('coordModeBadge');
  if (b) { b.textContent = 'Modo orientado por pergunta'; b.className = 'badge rounded-pill bg-info text-dark'; }
}

function resetCoordinatorSelects() {
  const q = qs('coordQuestionSelect');
  const p = qs('coordPeriodSelect');
  const c = qs('coordCursoSelect');
  if (q) q.innerHTML = '<option value="">— Nenhuma (configurar manualmente) —</option>';
  if (p) p.innerHTML = '<option value="">Todos os períodos</option>';
  if (c) c.innerHTML = '<option value="">Todos os cursos</option>';
  const btn = qs('btnCoordGerar');
  if (btn) btn.disabled = true;
  const h = qs('coordHint');
  if (h) { h.classList.add('d-none'); h.textContent = ''; }
  coordBadgeManual();
}

function loadCoordinatorMeta(filename) {
  resetCoordinatorSelects();
  if (!filename) return;
  fetch('/api/coordinator_meta', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
    .then(r => r.json())
    .then(js => {
      if (js.error) { return; }
      const qSel = qs('coordQuestionSelect');
      const pSel = qs('coordPeriodSelect');
      const cSel = qs('coordCursoSelect');
      (js.questions || []).forEach(q => {
        const o = document.createElement('option');
        o.value = q.id;
        o.textContent = q.label;
        o.title = q.description || '';
        qSel.appendChild(o);
      });
      (js.periods || []).forEach(p => {
        const o = document.createElement('option');
        o.value = p;
        o.textContent = p;
        pSel.appendChild(o);
      });
      (js.cursos || []).forEach(c => {
        const o = document.createElement('option');
        o.value = c;
        o.textContent = c;
        cSel.appendChild(o);
      });
      window.dispatchEvent(new CustomEvent('fmpCoordinatorMetaLoaded'));
    })
    .catch(() => {});
}

qs('arquivoSelect')?.addEventListener('change', () => {
  const fn = qs('arquivoSelect').value;
  if (!fn) resetCoordinatorSelects();
});

qs('coordQuestionSelect')?.addEventListener('change', () => {
  const fn = qs('dataOrigin').value === 'db' ? '__DB_DATA__' : qs('arquivoSelect').value;
  const qid = qs('coordQuestionSelect').value;
  const btn = qs('btnCoordGerar');
  const hint = qs('coordHint');
  if (qid) {
    coordBadgeOriented();
    const opt = qs('coordQuestionSelect').selectedOptions[0];
    if (hint && opt) {
      hint.textContent = opt.title || '';
      hint.classList.remove('d-none');
    }
  } else {
    coordBadgeManual();
    if (hint) hint.classList.add('d-none');
  }
  if (btn) btn.disabled = !(fn && qid);
});

function setCoordLoading(on) {
  const sp = qs('btnCoordSpinner');
  const lb = qs('btnCoordGerarLabel');
  const btn = qs('btnCoordGerar');
  const origin = qs('dataOrigin').value;
  const filename = origin === 'db' ? '__DB_DATA__' : qs('arquivoSelect').value;
  const qid = qs('coordQuestionSelect').value;
  if (sp) sp.classList.toggle('d-none', !on);
  if (lb) lb.textContent = on ? 'Gerando…' : 'Gerar resposta';
  if (btn) btn.disabled = on ? true : !(filename && qid);
}

function renderCoordinatorAnalysis(resp) {
  if (resp.report_type === 'general' && resp.general_report) {
    renderGeneralReport(resp);
    qs('btnSalvarTodos')?.classList.remove('d-none');
    return;
  }

  const container = qs('graficoContainer');
  container.innerHTML = '';

  const wrap = document.createElement('div');
  wrap.className = 'card border-info mb-4';
  wrap.innerHTML = `
    <div class="card-header text-white" style="background:#0B3353;">
      <strong>${escapeHtml(resp.title || '')}</strong>
      <div class="small opacity-75 mt-1">${escapeHtml(resp.period_label || '')}</div>
    </div>
    <div class="card-body">
      <p class="lead small mb-3">${escapeHtml(resp.insight || '')}</p>
      <div id="coordChartsMount"></div>
      <div id="coordExtrasMount"></div>
    </div>`;
  container.appendChild(wrap);

  const mount = qs('coordChartsMount');
  const leafletJobs = [];
  (resp.graficos || []).forEach((g, idx) => {
    const plotId = `chart_coord_${idx}`;
    const card = document.createElement('div');
    card.className = 'card mb-3';

    if (g.leaflet_cluster_map && g.leaflet_cluster_map.markers && g.leaflet_cluster_map.markers.length) {
      card.innerHTML = `
      <div class="card-header py-2 d-flex justify-content-between align-items-center" style="background:#f8f9fa;">
        <strong>${escapeHtml(g.title || '')}</strong>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="downloadLeafletMapPng('${plotId}')">📥 PNG</button>
      </div>
      <div class="card-body p-2">
        <div id="${plotId}" class="coord-leaflet-map"></div>
        <p class="small text-muted mt-2 mb-0">Mapa interativo (OpenStreetMap + clusters). O zoom acompanha só as cidades com cadastros. Arraste para mover; use scroll para zoom.</p>
      </div>`;
      mount.appendChild(card);
      leafletJobs.push({ plotId, spec: g.leaflet_cluster_map });
      return;
    }

    card.innerHTML = `
      <div class="card-header py-2 d-flex justify-content-between align-items-center" style="background:#f8f9fa;">
        <strong>${escapeHtml(g.title || '')}</strong>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="downloadPlotlyPNG('${plotId}')">📥 PNG</button>
      </div>
      <div class="card-body p-2"><div id="${plotId}" style="min-height:420px;"></div></div>`;
    mount.appendChild(card);
    try {
      const fig = g.fig || {};
      Plotly.react(plotId, fig.data || [], fig.layout || {}, { responsive: true });
    } catch (e) {
      const el = document.getElementById(plotId);
      if (el) el.innerHTML = `<pre class="text-danger">${e}</pre>`;
    }
  });

  if (leafletJobs.length) {
    ensureLeafletCluster(() => {
      leafletJobs.forEach(({ plotId, spec }) => {
        try {
          drawLeafletClusterMap(plotId, spec);
        } catch (e) {
          const el = document.getElementById(plotId);
          if (el) el.innerHTML = `<pre class="text-danger small">${e}</pre>`;
        }
      });
    });
  }

  const ex = resp.extras || {};
  const exMount = qs('coordExtrasMount');
  if (ex.card) {
    const c = document.createElement('div');
    c.className = 'row mb-3';
    c.innerHTML = `
      <div class="col-md-6">
        <div class="p-4 rounded-3 border bg-light text-center">
          <div class="text-muted small">${escapeHtml(ex.card.label || '')}</div>
          <div class="display-4 fw-bold text-primary">${escapeHtml(String(ex.card.value || ''))}</div>
          <div class="small text-secondary">${escapeHtml(ex.card.sub || '')}</div>
        </div>
      </div>`;
    exMount.appendChild(c);
  }
  if (ex.table_city_transport && ex.table_city_transport.length) {
    const t = document.createElement('div');
    t.className = 'table-responsive mb-3';
    let rows = ex.table_city_transport.map(r => `<tr><td>${escapeHtml(r.cidade)}</td><td>${r.quantidade}</td><td>${escapeHtml(r.principal_meio)}</td></tr>`).join('');
    t.innerHTML = `<h6 class="mt-3">Tabela complementar</h6><table class="table table-sm table-striped"><thead><tr><th>Cidade</th><th>Qtd. alunos</th><th>Principal meio</th></tr></thead><tbody>${rows}</tbody></table>`;
    exMount.appendChild(t);
  }
  if (ex.table_non_remat && ex.table_non_remat.length) {
    const box = document.createElement('div');
    box.className = 'mb-3';
    const csvB64 = ex.non_remat_csv_base64 || '';
    box.innerHTML = `
      <h6 class="mt-3">Lista de e-mails não rematriculados</h6>
      <p class="small text-muted">Alunos presentes no semestre anterior e sem rematrícula no último semestre de referência.</p>
      <input type="search" class="form-control form-control-sm mb-2" id="nonRematSearch" placeholder="Buscar e-mail ou curso…">
      <div class="table-responsive" style="max-height:280px;overflow:auto;"><table class="table table-sm" id="nonRematTable"><thead><tr><th>E-mail</th><th>Curso</th><th>Último período</th></tr></thead><tbody id="nonRematBody"></tbody></table></div>
      <button type="button" class="btn btn-outline-success btn-sm mt-2" id="btnNonRematCsv">Exportar CSV</button>`;
    exMount.appendChild(box);
    const tbody = qs('nonRematBody');
    function fillRows(list) {
      tbody.innerHTML = list.map(r => `<tr><td>${escapeHtml(r.email)}</td><td>${escapeHtml(r.curso)}</td><td>${escapeHtml(r.ultimo_periodo)}</td></tr>`).join('');
    }
    fillRows(ex.table_non_remat);
    qs('nonRematSearch')?.addEventListener('input', (ev) => {
      const term = ev.target.value.toLowerCase();
      const f = ex.table_non_remat.filter(r =>
        String(r.email).toLowerCase().includes(term) || String(r.curso).toLowerCase().includes(term));
      fillRows(f);
    });
    qs('btnNonRematCsv')?.addEventListener('click', () => {
      if (!csvB64) return;
      const bin = atob(csvB64);
      const blob = new Blob([bin], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'nao_rematriculados.csv';
      a.click();
      URL.revokeObjectURL(a.href);
    });
  }

  qs('btnSalvarTodos')?.classList.remove('d-none');
  scrollToSecaoResultado();
}

/**
 * Painel consolidado — Relatório Geral (pergunta orientada).
 */
function renderGeneralReport(resp) {
  const container = qs('graficoContainer');
  container.innerHTML = '';
  const gr = resp.general_report || {};
  const hl = gr.highlights || {};

  const wrap = document.createElement('div');
  wrap.className = 'card border-info mb-4';
  wrap.innerHTML = `
    <div class="card-header text-white" style="background:#0B3353;">
      <strong>${escapeHtml(resp.title || 'Relatório Geral')}</strong>
      <div class="small opacity-75 mt-1">${escapeHtml(resp.period_label || '')}</div>
    </div>
    <div class="card-body">
      <div class="alert alert-light border shadow-sm mb-3">
        <strong class="text-primary">Resumo executivo</strong>
        <p class="mb-0 small mt-2">${escapeHtml(resp.insight || '')}</p>
      </div>
      <div id="grSummaryCards" class="mb-3"></div>
      <div id="grHighlightsExtra" class="mb-4"></div>
      <div id="grBlocks"></div>
    </div>`;
  container.appendChild(wrap);

  const sumMount = qs('grSummaryCards');
  const row = document.createElement('div');
  row.className = 'row row-cols-2 row-cols-md-3 row-cols-lg-4 g-2';
  (gr.summary_cards || []).forEach((c) => {
    const col = document.createElement('div');
    col.className = 'col';
    col.innerHTML = `
      <div class="card h-100 border shadow-sm">
        <div class="card-body py-2 px-3">
          <div class="text-muted small">${escapeHtml(c.label)}</div>
          <div class="fs-5 fw-bold text-primary">${escapeHtml(String(c.value))}</div>
          ${c.sub ? `<div class="small text-secondary">${escapeHtml(c.sub)}</div>` : ''}
        </div>
      </div>`;
    row.appendChild(col);
  });
  sumMount.appendChild(row);

  const hx = qs('grHighlightsExtra');
  if (hl.totais_por_curso && Object.keys(hl.totais_por_curso).length) {
    const tbl = document.createElement('div');
    tbl.className = 'table-responsive';
    let body = Object.entries(hl.totais_por_curso)
      .map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="text-end">${v}</td></tr>`)
      .join('');
    tbl.innerHTML = `<h6 class="text-secondary">Totais por curso</h6><table class="table table-sm table-bordered mb-0"><thead><tr><th>Curso</th><th class="text-end">Alunos</th></tr></thead><tbody>${body}</tbody></table>`;
    hx.appendChild(tbl);
  }

  const blocksMount = qs('grBlocks');
  const leafletJobs = [];
  let plotIdx = 0;
  let mapIdx = 0;

  (gr.blocks || []).forEach((b) => {
    if (b.kind === 'section_title') {
      const h = document.createElement('h5');
      h.className = 'mt-4 mb-3 pb-2 border-bottom text-primary';
      h.textContent = b.text;
      blocksMount.appendChild(h);
      return;
    }
    if (b.kind === 'insight') {
      const p = document.createElement('p');
      p.className = 'small text-muted border-start border-3 border-info ps-2';
      p.textContent = b.text;
      blocksMount.appendChild(p);
      return;
    }
    if (b.kind === 'note') {
      const a = document.createElement('div');
      a.className = 'alert alert-warning small';
      a.textContent = b.text;
      blocksMount.appendChild(a);
      return;
    }
    if (b.kind === 'remat_card' && b.card) {
      const c = document.createElement('div');
      c.className = 'row mb-3';
      c.innerHTML = `
        <div class="col-md-6">
          <div class="p-4 rounded-3 border bg-light text-center">
            <div class="text-muted small">${escapeHtml(b.card.label || '')}</div>
            <div class="display-4 fw-bold text-primary">${escapeHtml(String(b.card.value || ''))}</div>
            <div class="small text-secondary">${escapeHtml(b.card.sub || '')}</div>
          </div>
        </div>`;
      blocksMount.appendChild(c);
      return;
    }
    if (b.kind === 'plotly' && b.fig) {
      const plotId = `gr_plot_${plotIdx++}`;
      const card = document.createElement('div');
      card.className = 'card mb-3';
      card.innerHTML = `
        <div class="card-header py-2 d-flex justify-content-between align-items-center" style="background:#f8f9fa;">
          <strong>${escapeHtml(b.title || '')}</strong>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="downloadPlotlyPNG('${plotId}')">📥 PNG</button>
        </div>
        <div class="card-body p-2"><div id="${plotId}" style="min-height:400px;"></div></div>`;
      blocksMount.appendChild(card);
      try {
        const fig = b.fig || {};
        Plotly.react(plotId, fig.data || [], fig.layout || {}, { responsive: true });
      } catch (e) {
        const el = document.getElementById(plotId);
        if (el) el.innerHTML = `<pre class="text-danger small">${e}</pre>`;
      }
      return;
    }
    if (b.kind === 'leaflet' && b.leaflet_cluster_map) {
      const plotId = `gr_map_${mapIdx++}`;
      const card = document.createElement('div');
      card.className = 'card mb-3';
      card.innerHTML = `
        <div class="card-header py-2 d-flex justify-content-between align-items-center" style="background:#f8f9fa;">
          <strong>${escapeHtml(b.title || '')}</strong>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="downloadLeafletMapPng('${plotId}')">📥 PNG</button>
        </div>
        <div class="card-body p-2">
          <div id="${plotId}" class="coord-leaflet-map"></div>
        </div>`;
      blocksMount.appendChild(card);
      leafletJobs.push({ plotId, spec: b.leaflet_cluster_map });
      return;
    }
    if (b.kind === 'table' && b.rows) {
      const cols = b.columns || Object.keys(b.rows[0] || {});
      const head = cols.map((c) => `<th>${escapeHtml(c)}</th>`).join('');
      const body = b.rows.map((r) =>
        `<tr>${cols.map((c) => `<td>${escapeHtml(String(r[c] ?? ''))}</td>`).join('')}</tr>`
      ).join('');
      const t = document.createElement('div');
      t.className = 'table-responsive mb-3';
      t.innerHTML = `<h6 class="mt-1">${escapeHtml(b.title || '')}</h6><table class="table table-sm table-striped"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
      blocksMount.appendChild(t);
      return;
    }
    if (b.kind === 'non_remat_table') {
      renderGeneralNonRematTable(blocksMount, b, resp);
    }
  });

  if (leafletJobs.length) {
    ensureLeafletCluster(() => {
      leafletJobs.forEach(({ plotId, spec }) => {
        try {
          drawLeafletClusterMap(plotId, spec);
        } catch (e) {
          const el = document.getElementById(plotId);
          if (el) el.innerHTML = `<pre class="text-danger small">${e}</pre>`;
        }
      });
    });
  }
  scrollToSecaoResultado();
}

function renderGeneralNonRematTable(mount, block, resp) {
  const pageSize = block.page_size || 25;
  const allRows = block.rows || [];
  const csvB64 = (resp.extras && resp.extras.non_remat_csv_base64) || '';

  const box = document.createElement('div');
  box.className = 'mb-3';
  box.innerHTML = `
    <input type="search" class="form-control form-control-sm mb-2 gr-nr-search" placeholder="Buscar e-mail, nome ou curso…">
    <div class="table-responsive" style="max-height:360px;overflow:auto;">
      <table class="table table-sm table-bordered"><thead><tr>
        <th>E-mail</th><th>Nome</th><th>Curso</th><th>Último período</th>
      </tr></thead><tbody class="gr-nr-tbody"></tbody></table>
    </div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mt-2">
      <span class="small text-muted gr-nr-pageinfo"></span>
      <div class="btn-group btn-group-sm">
        <button type="button" class="btn btn-outline-secondary gr-nr-prev">Anterior</button>
        <button type="button" class="btn btn-outline-secondary gr-nr-next">Próxima</button>
      </div>
    </div>
    <button type="button" class="btn btn-outline-success btn-sm mt-2 gr-nr-csv" ${!csvB64 ? 'disabled' : ''}>Exportar CSV</button>`;
  mount.appendChild(box);

  let page = 0;
  let filtered = allRows.slice();

  const tbody = box.querySelector('.gr-nr-tbody');
  const pageinfo = box.querySelector('.gr-nr-pageinfo');
  const inp = box.querySelector('.gr-nr-search');

  function paint() {
    const n = filtered.length;
    const maxPage = Math.max(0, Math.ceil(n / pageSize) - 1);
    page = Math.min(Math.max(0, page), maxPage);
    const slice = filtered.slice(page * pageSize, (page + 1) * pageSize);
    tbody.innerHTML = slice.map((r) =>
      `<tr><td>${escapeHtml(r.email || '')}</td><td>${escapeHtml(r.nome || '')}</td><td>${escapeHtml(r.curso || '')}</td><td>${escapeHtml(r.ultimo_periodo || '')}</td></tr>`
    ).join('');
    pageinfo.textContent = n
      ? `Mostrando ${page * pageSize + 1}–${Math.min((page + 1) * pageSize, n)} de ${n}`
      : 'Nenhuma linha';
  }

  inp.addEventListener('input', (ev) => {
    const term = String(ev.target.value || '').toLowerCase().trim();
    if (!term) {
      filtered = allRows.slice();
    } else {
      filtered = allRows.filter((r) =>
        String(r.email || '').toLowerCase().includes(term) ||
        String(r.nome || '').toLowerCase().includes(term) ||
        String(r.curso || '').toLowerCase().includes(term));
    }
    page = 0;
    paint();
  });

  box.querySelector('.gr-nr-prev').addEventListener('click', () => {
    page = Math.max(0, page - 1);
    paint();
  });
  box.querySelector('.gr-nr-next').addEventListener('click', () => {
    const maxPage = Math.max(0, Math.ceil(filtered.length / pageSize) - 1);
    page = Math.min(maxPage, page + 1);
    paint();
  });

  box.querySelector('.gr-nr-csv').addEventListener('click', () => {
    if (!csvB64) return;
    const bin = atob(csvB64);
    const blob = new Blob([bin], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'nao_rematriculados.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  });

  paint();
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

/** Export PNG do Google GeoChart (quando disponível). */
function ensureLeafletCluster(callback) {
  if (typeof L !== 'undefined' && L.markerClusterGroup) {
    callback();
    return;
  }
  const loadCss = (href) => {
    if (document.querySelector(`link[href="${href}"]`)) return;
    const l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = href;
    document.head.appendChild(l);
  };
  loadCss('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css');
  loadCss('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css');
  loadCss('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css');

  const s1 = document.createElement('script');
  s1.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  s1.onload = () => {
    const s2 = document.createElement('script');
    s2.src = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js';
    s2.onload = () => callback();
    s2.onerror = () => showError('Falha ao carregar MarkerCluster.');
    document.head.appendChild(s2);
  };
  s1.onerror = () => showError('Falha ao carregar Leaflet.');
  document.head.appendChild(s1);
}

function drawLeafletClusterMap(plotId, spec) {
  const el = document.getElementById(plotId);
  if (!el || !spec.markers || !spec.markers.length) return;
  el.style.height = '520px';
  el.style.width = '100%';
  el.innerHTML = '';
  if (window['_leafmap_' + plotId]) {
    try { window['_leafmap_' + plotId].remove(); } catch (e) { /* ignore */ }
    delete window['_leafmap_' + plotId];
  }

  const map = L.map(plotId, { scrollWheelZoom: true });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  const mcg = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 72,
    disableClusteringAtZoom: 14,
    spiderfyOnMaxZoom: true,
    zoomToBoundsOnClick: true,
    iconCreateFunction: function (cluster) {
      const count = cluster.getChildCount();
      const size = count < 10 ? 46 : count < 40 ? 54 : 62;
      return L.divIcon({
        html: `<div style="background:linear-gradient(160deg,#2563eb,#1e40af);color:#fff;border-radius:50%;width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;font-weight:800;border:3px solid #93c5fd;box-shadow:0 3px 14px rgba(37,99,235,.5)">${count}</div>`,
        className: 'coord-mcluster',
        iconSize: L.point(size, size)
      });
    }
  });

  spec.markers.forEach((m) => {
    const sz = Math.min(22 + Math.sqrt(m.count) * 2.8, 52);
    const ic = L.divIcon({
      className: 'coord-city-icon',
      html: `<div style="background:#4f46e5;color:#fff;border-radius:999px;min-width:${sz}px;height:${sz}px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #e0e7ff;padding:0 8px;box-shadow:0 2px 8px rgba(0,0,0,.15)">${m.count}</div>`,
      iconSize: [sz + 10, sz + 10],
      iconAnchor: [(sz + 10) / 2, (sz + 10) / 2]
    });
    const mk = L.marker([m.lat, m.lng], { icon: ic, title: m.city });
    mk.bindPopup(`<strong>${escapeHtml(m.city)}</strong><br>${m.count} aluno(s) únicos`);
    mcg.addLayer(mk);
  });

  map.addLayer(mcg);

  if (spec.markers.length === 1) {
    map.setView([spec.markers[0].lat, spec.markers[0].lng], 12);
  } else if (spec.bounds && spec.bounds.length === 2) {
    const b = L.latLngBounds(spec.bounds);
    map.fitBounds(b, { padding: [50, 50], maxZoom: 13 });
  }

  window['_leafmap_' + plotId] = map;
  setTimeout(() => map.invalidateSize(), 250);
}

function downloadLeafletMapPng(plotId) {
  const map = window['_leafmap_' + plotId];
  const el = document.getElementById(plotId);
  if (!el) return;
  if (map) map.invalidateSize();

  const run = () => {
    html2canvas(el, { useCORS: true, scale: 2, logging: false }).then((canvas) => {
      const a = document.createElement('a');
      a.href = canvas.toDataURL('image/png');
      a.download = plotId + '.png';
      a.click();
    }).catch(() => showError('Não foi possível exportar o mapa.'));
  };

  if (typeof html2canvas !== 'undefined') {
    run();
    return;
  }
  const s = document.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  s.onload = run;
  s.onerror = () => showError('Não foi possível carregar html2canvas.');
  document.head.appendChild(s);
}

qs('btnCoordGerar')?.addEventListener('click', () => {
  const origin = qs('dataOrigin').value;
  const filename = origin === 'db' ? '__DB_DATA__' : qs('arquivoSelect').value;
  const qid = qs('coordQuestionSelect').value;
  const periodo = qs('coordPeriodSelect').value || '';
  const curso = qs('coordCursoSelect').value || '';
  if (!filename || !qid) {
    showError('Selecione a base e uma pergunta.');
    return;
  }
  setCoordLoading(true);
  fetch('/api/coordinator_analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename,
      question_id: qid,
      periodo,
      curso
    })
  })
    .then(r => r.json())
    .then(js => {
      setCoordLoading(false);
      if (js.error) { showError(js.error); return; }
      renderCoordinatorAnalysis(js);
    })
    .catch(() => {
      setCoordLoading(false);
      showError('Erro ao gerar análise orientada.');
    });
});

