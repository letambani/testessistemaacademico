import { useCallback, useEffect, useState } from "react";
import { Button } from "@/app/components/ui/button";
import { Card, CardContent } from "@/app/components/ui/card";
import { fetchJson } from "@/lib/api";
import { normalizeCoordinatorResponse } from "@/lib/coordinatorResult";
import { cn } from "@/lib/utils";
import type { AnalysisResult } from "@/types/analysis";
import { ChevronDown, Loader2, Sparkles } from "lucide-react";

export interface IntelligentCrossingMeta {
  id: string;
  label: string;
  description?: string;
  chart_type?: string;
}

const PERIOD_ALL = "__period_all__";
const CURSO_ALL = "__curso_all__";

interface IntelligentCrossSectionProps {
  baseFilename?: string;
  period?: string;
  curso?: string;
  onResult: (result: AnalysisResult) => void;
  onError: (msg: string | null) => void;
  onLoading: (v: boolean) => void;
}

export function IntelligentCrossSection({
  baseFilename,
  period,
  curso,
  onResult,
  onError,
  onLoading,
}: IntelligentCrossSectionProps) {
  const [open, setOpen] = useState(false);
  const [catalog, setCatalog] = useState<IntelligentCrossingMeta[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetchJson<{ crossings: IntelligentCrossingMeta[] }>(
          "/api/intelligent_crossings",
        );
        setCatalog(Array.isArray(r.crossings) ? r.crossings : []);
      } catch {
        setCatalog([]);
      }
    })();
  }, []);

  const runCross = useCallback(
    async (crossingId: string) => {
      if (!baseFilename) {
        onError("Selecione uma base no Passo 1.");
        return;
      }
      setSelectedId(crossingId);
      setBusy(true);
      onLoading(true);
      onError(null);
      try {
        const raw = await fetchJson<unknown>("/api/intelligent_cross", {
          method: "POST",
          body: JSON.stringify({
            filename: baseFilename,
            crossing_id: crossingId,
            periodo:
              period && period !== PERIOD_ALL ? period : "",
            curso: curso && curso !== CURSO_ALL ? curso : "",
          }),
        });
        const normalized = normalizeCoordinatorResponse(raw);
        onResult(normalized);
      } catch (e) {
        onError(e instanceof Error ? e.message : "Falha ao gerar cruzamento.");
      } finally {
        setBusy(false);
        onLoading(false);
      }
    },
    [baseFilename, period, curso, onError, onLoading, onResult],
  );

  if (!catalog.length) return null;

  return (
    <div className="mt-4 rounded-xl border border-indigo-100 bg-gradient-to-b from-indigo-50/60 to-white shadow-sm">
      <Button
        type="button"
        variant="ghost"
        className="flex h-auto w-full items-center justify-between gap-2 rounded-xl px-4 py-3 text-left font-semibold text-indigo-950 hover:bg-indigo-50/80"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className="inline-flex items-center gap-2">
          <Sparkles className="h-4 w-4 shrink-0 text-indigo-600" aria-hidden />
          Cruzamento Inteligente de Dados
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-indigo-400 transition-transform",
            open && "rotate-180",
          )}
          aria-hidden
        />
      </Button>
      {open ? (
        <Card className="border-0 bg-transparent shadow-none">
          <CardContent className="space-y-3 px-4 pb-4 pt-0">
            <p className="text-xs leading-relaxed text-slate-600">
              Atalhos pensados para gestão: em um toque você vê cruzamentos úteis
              e um resumo em linguagem clara. Vale a mesma ideia das perguntas
              prontas — <strong>cada aluno conta uma vez</strong>, com a foto mais
              recente da situação — e respeita o período e o curso que você marcou
              acima.
            </p>
            {!baseFilename ? (
              <p className="rounded-lg border border-amber-100 bg-amber-50/80 px-3 py-2 text-xs text-amber-900">
                Primeiro escolha os dados no passo 1; aí estes atalhos liberam.
              </p>
            ) : null}
            <div className="grid gap-2 sm:grid-cols-2">
              {catalog.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  disabled={busy || !baseFilename}
                  onClick={() => void runCross(c.id)}
                  title={c.description}
                  className={cn(
                    "rounded-lg border bg-white p-3 text-left text-sm shadow-sm transition-all hover:border-indigo-300 hover:shadow-md",
                    selectedId === c.id &&
                      "border-indigo-500 ring-2 ring-indigo-200",
                    (!baseFilename || busy) && "opacity-50",
                  )}
                >
                  <span className="mb-1 inline-block rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-indigo-800">
                    {c.chart_type ?? "—"}
                  </span>
                  <div className="font-semibold text-slate-900">{c.label}</div>
                  {c.description ? (
                    <p className="mt-1 line-clamp-3 text-xs text-slate-600">
                      {c.description}
                    </p>
                  ) : null}
                  {busy && selectedId === c.id ? (
                    <span className="mt-2 inline-flex items-center gap-1 text-xs text-indigo-600">
                      <Loader2 className="h-3 w-3 animate-spin" aria-hidden />
                      Gerando…
                    </span>
                  ) : null}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
