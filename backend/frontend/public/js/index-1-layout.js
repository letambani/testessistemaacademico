/**
 * Reforços visuais do layout index-1.html (stepper, checklist, cartões).
 * Não altera a lógica principal em scripts.js.
 */
(function () {
  const qs = (id) => document.getElementById(id);

  const tipoLabel = (v) => {
    const m = { bar: "Barras", pie: "Pizza", line: "Linha", texto: "Relatório por extenso" };
    return m[v] || v || "—";
  };

  function togglePasso2Sections() {
    const coordQ = qs("coordQuestionSelect")?.value;
    const guided = Boolean(coordQ && String(coordQ).trim() !== "");
    /* Período/curso ficam visíveis também no modo manual (Cruzamento Inteligente usa os mesmos selects). */
    qs("fmpManualConfig")?.classList.toggle("d-none", guided);
    qs("fmpCoordPanel")?.classList.toggle("d-none", !guided);
  }

  function sync() {
    togglePasso2Sections();

    const origin = qs("dataOrigin")?.value;
    const arq = qs("arquivoSelect")?.value;
    const col = qs("colunaSelect")?.value;
    const tipo = qs("tipoSelect")?.value;
    const coordQ = qs("coordQuestionSelect")?.value;

    const step1 =
      origin === "db" ? true : Boolean(arq && String(arq).trim() !== "");

    const guided = Boolean(coordQ && String(coordQ).trim() !== "");
    const manualOk =
      !guided &&
      Boolean(col && String(col).trim() !== "" && tipo);
    const guidedOk = guided;
    const colunaCheckOk = guidedOk || manualOk;

    const ready = step1 && colunaCheckOk;

    const ciArq = qs("ci-arquivo");
    const ciCol = qs("ci-coluna");
    const ciPronto = qs("ci-pronto");
    if (ciArq) {
      ciArq.classList.toggle("fmp-ci-on", step1);
      ciArq.classList.toggle("fmp-ci-off", !step1);
    }
    if (ciCol) {
      ciCol.classList.toggle("fmp-ci-on", colunaCheckOk);
      ciCol.classList.toggle("fmp-ci-off", !colunaCheckOk);
    }
    if (ciPronto) {
      ciPronto.classList.toggle("fmp-ci-on", ready);
      ciPronto.classList.toggle("fmp-ci-off", !ready);
    }

    qs("checkStep1")?.classList.toggle("d-none", !step1);
    qs("cardFonte")?.classList.toggle("fmp-card-done", step1);

    qs("checkStep2")?.classList.toggle("d-none", !colunaCheckOk);
    qs("cardConfig")?.classList.toggle("fmp-card-done", colunaCheckOk);

    qs("arquivoSelect")?.classList.toggle("fmp-field-success", step1);
    qs("colunaSelect")?.classList.toggle(
      "fmp-field-success",
      !guided && Boolean(col && String(col).trim()),
    );
    qs("tipoSelect")?.classList.toggle(
      "fmp-field-success",
      !guided && Boolean(col && tipo),
    );
    qs("coordQuestionSelect")?.classList.toggle(
      "fmp-field-success",
      guided,
    );

    const hint = qs("fmpActionHint");
    if (hint) {
      if (!step1) {
        hint.textContent =
          "Comece escolhendo de onde vêm os dados e qual lista você quer analisar.";
      } else if (coordQ) {
        hint.textContent =
          "Ótimo! Agora é só tocar em «Gerar resposta» no cartão azul para ver o resultado.";
      } else if (manualOk) {
        hint.textContent = `Pronto para gerar: ${tipoLabel(tipo)} sobre «${col}».`;
      } else {
        hint.textContent =
          "Escolha uma pergunta pronta ou preencha coluna e tipo de gráfico para seguir.";
      }
    }

    const steps = document.querySelectorAll(".fmp-step");
    if (steps.length >= 3) {
      const setStep = (el, state) => {
        el.classList.remove("fmp-step-done", "fmp-step-active", "fmp-step-todo");
        el.classList.add(state);
      };
      const circle = (el, num, done, active) => {
        const c = el.querySelector(".fmp-step-circle");
        if (!c) return;
        c.innerHTML = done ? "OK" : String(num);
      };
      setStep(steps[0], step1 ? "fmp-step-done" : "fmp-step-active");
      circle(steps[0], 1, step1, !step1);

      const mid = step1 && !colunaCheckOk;
      const midDone = step1 && colunaCheckOk;
      setStep(steps[1], midDone ? "fmp-step-done" : mid ? "fmp-step-active" : "fmp-step-todo");
      circle(steps[1], 2, midDone, mid);

      const lastActive = step1 && colunaCheckOk;
      setStep(steps[2], lastActive ? "fmp-step-active" : "fmp-step-todo");
      circle(steps[2], 3, false, lastActive);
    }

    const lines = document.querySelectorAll(".fmp-step-line");
    if (lines[0]) lines[0].classList.toggle("fmp-line-done", step1);
    if (lines[1]) lines[1].classList.toggle("fmp-line-done", colunaCheckOk);
  }

  ["dataOrigin", "arquivoSelect", "arquivoCompare", "colunaSelect", "colunaGroupBy", "tipoSelect", "coordQuestionSelect", "coordPeriodSelect", "coordCursoSelect"].forEach((id) => {
    qs(id)?.addEventListener("change", sync);
  });

  window.addEventListener("fmpCoordinatorMetaLoaded", sync);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sync);
  } else {
    sync();
  }
})();
