// scripts.js (index.html)
// requer Plotly e Bootstrap bundle pré-carregados.

// util
const qs = id => document.getElementById(id);
const showError = msg => alert(msg);

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
