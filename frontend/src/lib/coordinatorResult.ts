import type { AnalysisResult, GraficoPayload, PlotlyFigure } from "@/types/analysis";

type Block = {
  kind?: string;
  title?: string;
  fig?: PlotlyFigure;
  text?: string;
};

export function normalizeCoordinatorResponse(raw: unknown): AnalysisResult {
  const d = raw as Record<string, unknown>;
  const err = d.error;
  if (typeof err === "string" && err.trim()) {
    throw new Error(err);
  }

  const insight =
    typeof d.insight === "string" ? d.insight : undefined;
  const title = typeof d.title === "string" ? d.title : undefined;
  const period_label =
    typeof d.period_label === "string" ? d.period_label : undefined;

  const direct = d.graficos;
  if (Array.isArray(direct) && direct.length > 0) {
    return {
      kind: "coordinator",
      title,
      insight,
      graficos: direct as GraficoPayload[],
      period_label,
      extras: d.extras as Record<string, unknown> | undefined,
      mode: typeof d.mode === "string" ? d.mode : undefined,
    };
  }

  const gr = d.general_report as
    | { blocks?: Block[] }
    | undefined;
  const blocks = gr?.blocks;
  if (Array.isArray(blocks)) {
    const graficos: GraficoPayload[] = [];
    for (const b of blocks) {
      if (b?.kind === "plotly" && b.fig) {
        graficos.push({
          title: b.title ?? "Gráfico",
          fig: b.fig,
        });
      }
    }
    return {
      kind: "coordinator",
      title,
      insight,
      graficos,
      period_label,
      extras: d.extras as Record<string, unknown> | undefined,
      mode: typeof d.mode === "string" ? d.mode : undefined,
    };
  }

  return {
    kind: "coordinator",
    title,
    insight,
    graficos: [],
    period_label,
    extras: d.extras as Record<string, unknown> | undefined,
    mode: typeof d.mode === "string" ? d.mode : undefined,
  };
}
