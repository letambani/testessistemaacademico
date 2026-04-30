/** Plotly figure JSON (subset) */
export interface PlotlyFigure {
  data: object[];
  layout: Record<string, unknown>;
}

export interface GraficoPayload {
  title: string;
  fig: PlotlyFigure;
}

export interface GraficoApiResponse {
  graficos: GraficoPayload[];
}

export interface CoordinatorQuestion {
  id: string;
  label: string;
  description?: string;
  chart_type?: string;
}

/** Resposta de /api/columns (inclui metadados para perguntas orientadas). */
export interface ColumnsApiResponse {
  columns: Array<{
    name: string;
    is_numeric: boolean;
    unique_values_count: number;
    sample_values: string[];
  }>;
  questions?: CoordinatorQuestion[];
  periods?: string[];
  cursos?: string[];
}

export interface CoordinatorMetaResponse {
  questions: CoordinatorQuestion[];
  periods: string[];
  cursos: string[];
}

export type ManualChartType = "bar" | "pie" | "line" | "report";

export type AnalysisResult =
  | {
      kind: "manual";
      graficos: GraficoPayload[];
      relatorio_texto?: string;
    }
  | {
      kind: "coordinator";
      title?: string;
      insight?: string;
      graficos: GraficoPayload[];
      extras?: Record<string, unknown>;
      period_label?: string;
      mode?: string;
    };
