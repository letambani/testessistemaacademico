import { PlotlyChart } from "@/app/components/PlotlyChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import type { AnalysisResult } from "@/types/analysis";
import { BarChart3, Loader2 } from "lucide-react";

interface ResultsPanelProps {
  result: AnalysisResult | null;
  loading?: boolean;
  error?: string | null;
}

export function ResultsPanel({
  result,
  loading = false,
  error = null,
}: ResultsPanelProps) {
  return (
    <section
      className="mt-8 border-t border-slate-200 pt-8"
      aria-labelledby="results-heading"
    >
      <h2
        id="results-heading"
        className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900"
      >
        <BarChart3 className="h-5 w-5 text-[#0B3353]" aria-hidden />
        Resultado
      </h2>

      {loading ? (
        <Card className="border-dashed border-slate-300 shadow-sm">
          <CardContent className="flex items-center gap-3 py-12 text-slate-600">
            <Loader2 className="h-6 w-6 shrink-0 animate-spin" aria-hidden />
            <p className="text-sm">Gerando análise…</p>
          </CardContent>
        </Card>
      ) : null}

      {!loading && error ? (
        <Card className="border-red-200 bg-red-50 shadow-sm">
          <CardContent className="py-6 text-sm text-red-800">
            {error}
          </CardContent>
        </Card>
      ) : null}

      {!loading && !error && !result ? (
        <Card className="border-dashed border-slate-300 bg-slate-50/80 shadow-sm">
          <CardContent className="py-12 text-center text-sm text-slate-600">
            Configure os dados e clique em &quot;Gerar Análise&quot; para
            visualizar gráficos e relatórios aqui.
          </CardContent>
        </Card>
      ) : null}

      {!loading && !error && result?.kind === "manual" && result.relatorio_texto ? (
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="text-base">Relatório textual</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-xs text-slate-800">
              {result.relatorio_texto}
            </pre>
          </CardContent>
        </Card>
      ) : null}

      {!loading && !error && result?.graficos?.length ? (
        <div className="flex flex-col gap-8">
          {result.kind === "coordinator" && result.insight ? (
            <Card className="border-sky-100 bg-sky-50/80 shadow-sm">
              <CardContent className="py-4 text-sm text-slate-800">
                <p className="font-medium text-[#0B3353]">Insight</p>
                <p className="mt-2 leading-relaxed">{result.insight}</p>
                {result.period_label ? (
                  <p className="mt-2 text-xs text-slate-600">
                    {result.period_label}
                  </p>
                ) : null}
              </CardContent>
            </Card>
          ) : null}
          {result.graficos.map((g, i) => (
            <PlotlyChart
              key={`${g.title}-${i}`}
              title={g.title}
              figure={g.fig}
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}
