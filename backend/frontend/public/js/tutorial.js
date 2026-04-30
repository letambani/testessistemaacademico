// static/js/tutorial.js — tour "Como usar" (linguagem simples, foco em benefícios)

(function () {
  function qs(sel) {
    return document.querySelector(sel);
  }

  function addStep(tour, cfg) {
    const el = cfg.attachTo ? qs(cfg.attachTo.element) : null;
    if (cfg.requireElement && !el) return;
    const step = {
      id: cfg.id,
      title: cfg.title,
      text: cfg.text,
      buttons: cfg.buttons || [
        { text: "Anterior", action: tour.back },
        { text: "Continuar", action: tour.next },
      ],
    };
    if (el && cfg.attachTo) {
      step.attachTo = cfg.attachTo;
    }
    tour.addStep(step);
  }

  function buildTour() {
    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: {
        classes: "shadow-lg bg-white p-3 rounded",
        scrollTo: { behavior: "smooth", block: "center" },
        cancelIcon: { enabled: true },
      },
    });

    tour.addStep({
      id: "welcome",
      title: "Olá! Bem-vindo às análises",
      text: `
        Aqui você transforma informações dos alunos em <b>gráficos claros</b> e em respostas prontas
        para reuniões e relatórios — sem precisar ser expert em planilhas.
        <br><br>
        Em poucos passos: <b>o que analisar</b>, <b>como ver</b> (pergunta pronta ou montagem manual)
        e <b>gerar o resultado</b>. Pode fechar este guia a qualquer momento pelo X.
        <br><br>
        Toque em <b>Continuar</b> para começar o passeio pela tela.
      `,
      buttons: [{ text: "Continuar", action: tour.next }],
    });

    addStep(tour, {
      id: "nav-matricula",
      title: "Matrícula na palma da mão",
      text: `
        O botão <b>Matrícula</b> abre o formulário oficial em uma nova aba, para cadastros
        e renovações. Quando esses dados já estiverem na faculdade, você pode analisá-los aqui
        escolhendo a opção de dados ligados à faculdade no primeiro bloco da tela.
      `,
      attachTo: { element: "#fmpTourNavMatricula", on: "bottom" },
      requireElement: true,
    });

    addStep(tour, {
      id: "passo1-card",
      title: "Primeiro: de onde vêm os dados",
      text: `
        Neste cartão você diz <b>qual conjunto de informações</b> quer usar e qual lista
        será a principal. Também dá para comparar dois conjuntos, lado a lado, quando fizer sentido.
        <br>No topo da página, <b>Atualizar</b> renova a lista se algo novo tiver sido enviado.
      `,
      attachTo: { element: "#cardFonte", on: "bottom" },
      requireElement: true,
    });

    addStep(tour, {
      id: "origem",
      title: "Escolha o tipo de informação",
      text: `
        Comece por aqui: planilhas que já estão no sistema ou a visão integrada com os dados
        de matrícula da faculdade. Depois disso, escolha a lista certa — assim os gráficos
        e perguntas aparecem alinhados com o que você selecionou.
      `,
      attachTo: { element: "#dataOrigin", on: "bottom" },
      requireElement: true,
    });

    addStep(tour, {
      id: "arquivo-base",
      title: "A lista principal",
      text: `
        É o “arquivo estrela” da sua análise: tudo o que vier abaixo se baseia nessa escolha.
        Se tiver dúvida, peça ajuda ao setor que envia as planilhas ou use <b>Atualizar</b>.
      `,
      attachTo: { element: "#arquivoSelect", on: "right" },
      requireElement: true,
    });

    addStep(tour, {
      id: "comparar",
      title: "Quer comparar com outra lista?",
      text: `
        Opcional. Serve para ver diferenças entre dois momentos ou duas bases, sempre com a mesma
        pergunta em mente. Mais embaixo existe também o botão <b>Gerar e Comparar</b> para ver tudo de uma vez.
      `,
      attachTo: { element: "#arquivoCompare", on: "right" },
      requireElement: true,
    });

    addStep(tour, {
      id: "passo2-card",
      title: "Segundo: o que você quer saber",
      text: `
        Três caminhos simples: <b>perguntas prontas</b> (o sistema monta o gráfico para você),
        <b>atalhos inteligentes</b> (cruzamentos já pensados para gestão) ou <b>montar na mão</b>
        (escolhe o assunto e o tipo de gráfico). Período e curso ajudam a focar só o que importa agora.
      `,
      attachTo: { element: "#cardConfig", on: "left" },
      requireElement: true,
    });

    addStep(tour, {
      id: "pergunta-orientada",
      title: "Perguntas prontas para coordenação",
      text: `
        Escolha uma pergunta na lista e siga o botão azul <b>Gerar resposta</b> quando ele aparecer.
        Deixe em “Nenhuma” se preferir montar sua própria visualização no cartão abaixo.
      `,
      attachTo: { element: "#coordQuestionSelect", on: "right" },
      requireElement: true,
    });

    addStep(tour, {
      id: "periodo-curso",
      title: "Foco por período ou curso",
      text: `
        Opcional e bem prático: restringe a análise a um semestre ou a um curso, para apresentações
        mais objetivas e conversas mais tranquilas com sua equipe.
      `,
      attachTo: { element: "#coordPeriodSelect", on: "right" },
      requireElement: true,
    });

    addStep(tour, {
      id: "cruzamento-inteligente",
      title: "Atalhos que economizam tempo",
      text: `
        Abra <b>Cruzamento inteligente</b> e toque em um cartão: em segundos você vê gráficos
        úteis e um texto que resume o que os números estão dizendo — ideal para quem precisa
        de clareza rápida, sem montar tudo do zero.
      `,
      attachTo: { element: "#fmpTourIcAccordion", on: "bottom" },
      requireElement: true,
    });

    addStep(tour, {
      id: "manual-coluna",
      title: "Prefere personalizar?",
      text: `
        Sem pergunta pronta? Escolha o tema (ex.: cidade, renda, transporte), se quiser agrupar
        por outro critério e o formato do gráfico — barras, pizza, linha ou texto corrido para imprimir ou compartilhar.
      `,
      attachTo: { element: "#colunaSelect", on: "right" },
      requireElement: true,
    });

    addStep(tour, {
      id: "filtros-avancados",
      title: "Refinar com calma",
      text: `
        Abra <b>Filtros avançados</b> para marcar só os valores que interessam (por exemplo,
        um campus ou um perfil). Isso deixa o resultado mais limpo para decisão.
      `,
      attachTo: { element: "#fmpTourFiltros", on: "top" },
      requireElement: true,
    });

    addStep(tour, {
      id: "gerar",
      title: "Hora de ver o resultado",
      text: `
        No modo personalizado, use <b>Gerar análise</b> quando estiver tudo preenchido.
        Com pergunta pronta, o passo é <b>Gerar resposta</b> no cartão azul. Em seguida o resultado aparece mais abaixo, pronto para explorar.
      `,
      attachTo: { element: "#fmpTourActionBar", on: "top" },
      requireElement: true,
    });

    addStep(tour, {
      id: "resultado",
      title: "Seus gráficos, do seu jeito",
      text: `
        Aqui aparecem as visualizações: dá para ampliar, mover e baixar imagem quando houver botão de download.
        É o material que você pode levar para reunião ou incluir em apresentações.
      `,
      attachTo: { element: "#graficoContainer", on: "top" },
      requireElement: true,
    });

    addStep(tour, {
      id: "duvidas-chat",
      title: "Ainda tem dúvida?",
      text: `
        O cantinho <b>Dúvidas?</b> abre um assistente para perguntas sobre os dados — como ter
        alguém do time ao lado explicando em linguagem simples (precisa estar conectado ao sistema).
      `,
      attachTo: { element: "#chatbot-button", on: "left" },
      requireElement: true,
    });

    addStep(tour, {
      id: "upload-admin",
      title: "Envio de planilhas (quem tem permissão)",
      text: `
        Alguns perfis veem <b>Enviar CSV</b> e gestão de arquivos: serve para colocar novas planilhas
        no ambiente e manter tudo organizado para a equipe analisar.
      `,
      attachTo: { element: "#btnUploadVisible", on: "bottom" },
      requireElement: true,
    });

    addStep(tour, {
      id: "salvar-todos",
      title: "Guardar tudo de uma vez",
      text: `
        Em relatórios grandes, pode aparecer <b>Salvar todos</b> para baixar os gráficos juntos —
        prático para arquivo ou envio por e-mail.
      `,
      attachTo: { element: "#btnSalvarTodos", on: "left" },
      requireElement: true,
    });

    tour.addStep({
      id: "final",
      title: "Por hoje é isso!",
      text: `
        Obrigado por seguir o tour. Quer rever? É só clicar de novo em <b>Como usar</b> no topo.
        Boa análise — e boas decisões com os dados da FMP.
      `,
      buttons: [{ text: "Fechar", action: tour.complete }],
    });

    return tour;
  }

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("btnTutorial");
    if (!btn) return;

    btn.addEventListener("click", function () {
      if (typeof Shepherd === "undefined") {
        window.alert(
          "Não foi possível abrir o guia. Verifique sua internet e atualize a página.",
        );
        return;
      }
      try {
        const tour = buildTour();
        tour.start();
      } catch (e) {
        console.error(e);
        window.alert(
          "O guia não abriu desta vez. Atualize a página e tente de novo, ou fale com o suporte da faculdade.",
        );
      }
    });
  });
})();
