// static/js/tutorial.js

document.addEventListener("DOMContentLoaded", function () {

    // -----------------------------
    // CONFIGURAÇÃO DO TUTORIAL
    // -----------------------------
    const tour = new Shepherd.Tour({
        useModalOverlay: true,
        defaultStepOptions: {
            classes: "shadow-lg bg-white p-3 rounded",
            scrollTo: true,
            cancelIcon: { enabled: true }
        }
    });

    // -----------------------------
    // PASSO 1 — Bem-vindo
    // -----------------------------
    tour.addStep({
        id: "welcome",
        title: "Bem-vindo ao Sistema de Análises 📊",
        text: `
            Este tutorial irá te guiar por todas as funcionalidades:
            upload, filtros, geração de gráficos e comparações.
            <br><br>
            Clique em <b>Próximo</b> para continuar.
        `,
        buttons: [
            { text: "Próximo", action: tour.next }
        ]
    });

    // -----------------------------
    // PASSO 2 — Botão de Upload
    // -----------------------------
    if (document.querySelector("#btnUploadVisible")) {
        tour.addStep({
            id: "upload-btn",
            title: "Enviar Arquivo",
            text: `
                Clique aqui para fazer upload de arquivos CSV.
                Somente usuários autorizados conseguem usar esta função.
            `,
            attachTo: { element: "#btnUploadVisible", on: "bottom" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 3 — Campo de arquivo base
    // -----------------------------
    if (document.querySelector("#arquivoSelect")) {
        tour.addStep({
            id: "file-base",
            title: "Arquivo Base",
            text: `
                Aqui você escolhe o arquivo que será usado como base da análise.
            `,
            attachTo: { element: "#arquivoSelect", on: "right" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 4 — Coluna principal
    // -----------------------------
    if (document.querySelector("#colunaSelect")) {
        tour.addStep({
            id: "main-column",
            title: "Coluna Principal",
            text: `
                Escolha a coluna que será analisada — exemplo:
                <b>curso, idade, cidade, setor</b>.
            `,
            attachTo: { element: "#colunaSelect", on: "right" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 5 — Agrupar por
    // -----------------------------
    if (document.querySelector("#colunaGroupBy")) {
        tour.addStep({
            id: "group-by",
            title: "Agrupar por (opcional)",
            text: `
                Se quiser análises por grupo, escolha aqui.
                <br>
                Exemplos: <b>campus</b>, <b>turno</b>, <b>setor</b>.
            `,
            attachTo: { element: "#colunaGroupBy", on: "right" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 6 — Tipo de Gráfico
    // -----------------------------
    if (document.querySelector("#tipoSelect")) {
        tour.addStep({
            id: "chart-type",
            title: "Tipo de Gráfico",
            text: `
                Escolha o tipo de visualização: barras, pizza, linha ou histograma.
            `,
            attachTo: { element: "#tipoSelect", on: "right" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 7 — Filtros
    // -----------------------------
    if (document.querySelector("#filtersArea")) {
        tour.addStep({
            id: "filters",
            title: "Filtros personalizados",
            text: `
                Quando você escolhe um arquivo e uma coluna,
                todos os valores possíveis aparecem aqui como filtros.
                <br><br>
                Marque/desmarque para refinar sua análise.
            `,
            attachTo: { element: "#filtersArea", on: "left" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 8 — Gerar gráfico
    // -----------------------------
    if (document.querySelector("#btnGerar")) {
        tour.addStep({
            id: "generate",
            title: "Gerar Gráfico",
            text: `
                Após configurar tudo, clique aqui.
                <br>
                Se houver agrupamento, vários gráficos serão gerados.
            `,
            attachTo: { element: "#btnGerar", on: "bottom" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 9 — Área dos Gráficos
    // -----------------------------
    if (document.querySelector("#graficoContainer")) {
        tour.addStep({
            id: "charts-area",
            title: "Visualização dos Gráficos",
            text: `
                Os gráficos aparecem nesta área.
                <br>
                Utilize as ferramentas do Plotly:
                zoom, reset, mover, salvar como PNG, etc.
            `,
            attachTo: { element: "#graficoContainer", on: "top" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 10 — Comparação entre arquivos
    // -----------------------------
    if (document.querySelector("#arquivoCompare")) {
        tour.addStep({
            id: "compare-files",
            title: "Comparar Arquivos",
            text: `
                Selecione um arquivo aqui para compará-lo
                com o arquivo base.
            `,
            attachTo: { element: "#arquivoCompare", on: "right" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    if (document.querySelector("#btnGerarComparar")) {
        tour.addStep({
            id: "btn-compare",
            title: "Gerar Comparação",
            text: `
                Clique aqui para gerar gráficos comparativos
                e visualizar a diferença percentual.
            `,
            attachTo: { element: "#btnGerarComparar", on: "bottom" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO 11 — Baixar Gráficos
    // -----------------------------
    if (document.querySelector("#btnSalvarTodos")) {
        tour.addStep({
            id: "download",
            title: "Salvar Todos os Gráficos",
            text: `
                Clique aqui para baixar todos os gráficos gerados.
                <br>
                Cada card também possui um botão próprio de download.
            `,
            attachTo: { element: "#btnSalvarTodos", on: "left" },
            buttons: [
                { text: "Voltar", action: tour.back },
                { text: "Próximo", action: tour.next }
            ]
        });
    }

    // -----------------------------
    // PASSO FINAL
    // -----------------------------
    tour.addStep({
        id: "final",
        title: "Fim do Tutorial 🎉",
        text: `
            Agora você conhece todas as funcionalidades!
            <br><br>
            Se precisar rever, clique no botão
            <b>❓ Tutorial</b> no topo da tela.
        `,
        buttons: [
            { text: "Repetir Tutorial", action: () => tour.show(0) },
            { text: "Concluir", action: tour.complete }
        ]
    });

    // -----------------------------
    // BOTÃO PARA INICIAR MANUALMENTE
    // -----------------------------
    const btn = document.getElementById("btnTutorial");
    if (btn) btn.addEventListener("click", () => tour.start());

});
