import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { fetchJson } from "@/lib/api";
import { normalizeCoordinatorResponse } from "@/lib/coordinatorResult";
import { cn } from "@/lib/utils";
import type {
  AnalysisResult,
  CoordinatorMetaResponse,
  GraficoApiResponse,
  ManualChartType,
} from "@/types/analysis";
import {
  BarChart3,
  CheckCircle2,
  ChevronDown,
  Database,
  Filter,
  GitCompare,
  LineChart,
  Link2,
  PieChart,
  Settings,
  Table2,
} from "lucide-react";

const PLACEHOLDER = "Selecione uma opção";
const GUIDED_NONE = "__guided_none__";
const COMPARE_NONE = "__compare_none__";
const GROUP_NONE = "__group_none__";
const PERIOD_ALL = "__period_all__";
const CURSO_ALL = "__curso_all__";

type DataOrigin = "csv" | "database" | "api";

interface ColumnRow {
  name: string;
  is_numeric: boolean;
  unique_values_count: number;
  sample_values: string[];
}

interface ColumnsResponse {
  columns: ColumnRow[];
}

interface ControlPanelProps {
  onAnalysisComplete: (result: AnalysisResult | null) => void;
  onLoading: (v: boolean) => void;
  onError: (msg: string | null) => void;
}

function resolveFilename(
  origin: DataOrigin | undefined,
  selectedFile: string | undefined,
): string | undefined {
  if (!origin) return undefined;
  if (origin === "database") return "__DB_DATA__";
  return selectedFile;
}

function StepCircle({
  step,
  label,
  state,
}: {
  step: number;
  label: string;
  state: "done" | "current" | "todo";
}) {
  return (
    <div className="flex min-w-0 flex-1 flex-col items-center gap-2">
      <div
        className={cn(
          "flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all duration-200",
          state === "done" &&
            "border-emerald-500 bg-emerald-50 text-emerald-700",
          state === "current" &&
            "border-sky-500 bg-sky-50 text-[#0B3353] shadow-sm",
          state === "todo" && "border-slate-200 bg-white text-slate-400",
        )}
        aria-current={state === "current" ? "step" : undefined}
      >
        {state === "done" ? (
          <CheckCircle2 className="h-6 w-6 text-emerald-600" aria-hidden />
        ) : (
          <span>{step}</span>
        )}
      </div>
      <span
        className={cn(
          "max-w-[7rem] text-center text-[11px] font-semibold leading-tight sm:max-w-none sm:text-xs",
          state === "done" && "text-emerald-700",
          state === "current" && "text-[#0B3353]",
          state === "todo" && "text-slate-400",
        )}
      >
        {label}
      </span>
    </div>
  );
}

function StepConnector({ done }: { done: boolean }) {
  return (
    <div
      className={cn(
        "hidden h-0.5 min-w-[1rem] flex-1 self-center sm:block",
        done ? "bg-emerald-400" : "bg-slate-200",
      )}
      aria-hidden
    />
  );
}

function fieldSuccessClass(valid: boolean): string {
  return cn(
    valid &&
      "border-emerald-500 bg-emerald-50 ring-1 ring-emerald-200/80 hover:bg-emerald-50/90",
  );
}

const CHART_OPTIONS: {
  value: ManualChartType;
  label: string;
  icon: ReactNode;
}[] = [
  { value: "bar", label: "Barras", icon: <BarChart3 className="h-4 w-4" /> },
  { value: "pie", label: "Pizza", icon: <PieChart className="h-4 w-4" /> },
  {
    value: "line",
    label: "Linha",
    icon: <LineChart className="h-4 w-4" />,
  },
  {
    value: "report",
    label: "Relatório",
    icon: <Table2 className="h-4 w-4" />,
  },
];

export function ControlPanel({
  onAnalysisComplete,
  onLoading,
  onError,
}: ControlPanelProps) {
  const [files, setFiles] = useState<string[]>([]);
  const [listError, setListError] = useState<string | null>(null);

  const [origin, setOrigin] = useState<DataOrigin | undefined>();
  const [baseFile, setBaseFile] = useState<string | undefined>();
  const [compareFile, setCompareFile] = useState<string | undefined>();

  const [guidedId, setGuidedId] = useState<string | undefined>();
  const [meta, setMeta] = useState<CoordinatorMetaResponse | null>(null);

  const [mainColumn, setMainColumn] = useState<string | undefined>();
  const [groupBy, setGroupBy] = useState<string | undefined>();
  const [chartType, setChartType] = useState<ManualChartType | undefined>();

  const [period, setPeriod] = useState<string | undefined>();
  const [curso, setCurso] = useState<string | undefined>();

  const [columns, setColumns] = useState<ColumnRow[]>([]);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const csvFiles = useMemo(
    () => files.filter((f) => f.toLowerCase().endsWith(".csv")),
    [files],
  );
  const apiFiles = useMemo(
    () =>
      files.filter(
        (f) =>
          f.startsWith("🟢") || f.startsWith("🔵") || f.startsWith("🟡"),
      ),
    [files],
  );

  const baseOptions = useMemo(() => {
    if (origin === "csv") return csvFiles;
    if (origin === "api") return apiFiles;
    return [];
  }, [origin, csvFiles, apiFiles]);

  const baseFilename = useMemo(
    () => resolveFilename(origin, baseFile),
    [origin, baseFile],
  );

  const step1Done = Boolean(
    origin &&
      (origin === "database" ||
        (origin === "csv" && baseFile) ||
        (origin === "api" && baseFile)),
  );

  const step2Done = guidedId !== undefined;

  const needsStep3 = guidedId === GUIDED_NONE;
  const step3Done =
    !needsStep3 || Boolean(mainColumn && chartType);

  const canGenerate = step1Done && step2Done && step3Done;

  useEffect(() => {
    void (async () => {
      try {
        const data = await fetchJson<{ files: string[] }>("/list_files");
        setFiles(data.files ?? []);
        setListError(null);
      } catch (e) {
        setListError(
          e instanceof Error
            ? e.message
            : "Não foi possível carregar arquivos. Faça login no servidor Flask (sessão) ou verifique se o proxy está ativo.",
        );
      }
    })();
  }, []);

  useEffect(() => {
    if (!baseFilename) {
      setColumns([]);
      setMainColumn(undefined);
      setGroupBy(undefined);
      setMeta(null);
      return;
    }
    void (async () => {
      try {
        const res = await fetchJson<ColumnsResponse>("/api/columns", {
          method: "POST",
          body: JSON.stringify({ filename: baseFilename }),
        });
        setColumns(res.columns ?? []);
      } catch {
        setColumns([]);
      }
    })();
  }, [baseFilename]);

  useEffect(() => {
    if (!baseFilename || !step1Done) {
      setMeta(null);
      return;
    }
    void (async () => {
      try {
        const m = await fetchJson<CoordinatorMetaResponse>(
          "/api/coordinator_meta",
          {
            method: "POST",
            body: JSON.stringify({ filename: baseFilename }),
          },
        );
        setMeta(m);
      } catch {
        setMeta(null);
      }
    })();
  }, [baseFilename, step1Done]);

  useEffect(() => {
    if (guidedId && guidedId !== GUIDED_NONE) {
      setPeriod(undefined);
      setCurso(undefined);
    }
  }, [guidedId]);

  useEffect(() => {
    if (guidedId === GUIDED_NONE) {
      setGroupBy((g) => g ?? GROUP_NONE);
    }
  }, [guidedId]);

  const questions = meta?.questions ?? [];

  const configurationComplete = Boolean(
    step1Done &&
      step2Done &&
      (!needsStep3 || Boolean(mainColumn && chartType)),
  );

  const getStepVisual = (
    n: 1 | 2 | 3,
  ): "done" | "current" | "todo" => {
    if (n === 1) {
      if (!step1Done) return "current";
      return "done";
    }
    if (n === 2) {
      if (!step1Done) return "todo";
      if (!configurationComplete) return "current";
      return "done";
    }
    if (!step1Done) return "todo";
    if (!configurationComplete) return "todo";
    return "current";
  };

  const footerSubline = useMemo(() => {
    if (!step1Done) return "Selecione origem e base para continuar.";
    if (!step2Done) return "Escolha uma pergunta orientada ou o modo manual.";
    if (needsStep3 && !step3Done) {
      return "Defina coluna principal e tipo de visualização.";
    }
    if (guidedId && guidedId !== GUIDED_NONE) {
      const q = questions.find((x) => x.id === guidedId);
      return q ? `Análise orientada: ${q.label}` : "Análise orientada selecionada.";
    }
    const tipo =
      CHART_OPTIONS.find((c) => c.value === chartType)?.label ?? "—";
    return `Gráfico de ${tipo} — Coluna: ${mainColumn ?? "—"}`;
  }, [
    step1Done,
    step2Done,
    needsStep3,
    step3Done,
    guidedId,
    chartType,
    mainColumn,
    questions,
  ]);

  const handleGenerate = useCallback(async () => {
    if (!canGenerate || !baseFilename) return;
    onError(null);
    onLoading(true);
    onAnalysisComplete(null);
    try {
      if (guidedId && guidedId !== GUIDED_NONE) {
        const raw = await fetchJson<unknown>("/api/coordinator_analysis", {
          method: "POST",
          body: JSON.stringify({
            filename: baseFilename,
            question_id: guidedId,
            periodo:
              period && period !== PERIOD_ALL ? period : "",
            curso: curso && curso !== CURSO_ALL ? curso : "",
          }),
        });
        const normalized = normalizeCoordinatorResponse(raw);
        onAnalysisComplete(normalized);
      } else {
        const compare =
          compareFile && compareFile !== COMPARE_NONE
            ? compareFile
            : undefined;
        const payload: Record<string, unknown> = {
          filename: baseFilename,
          compare_with: compare,
          coluna: mainColumn,
          tipo:
            chartType === "report"
              ? "bar"
              : chartType ?? "bar",
          modo: chartType === "report" ? "texto" : "grafico",
          filtros: {},
        };
        if (groupBy && groupBy !== GROUP_NONE) {
          payload.groupby = groupBy;
        }
        const raw = await fetchJson<GraficoApiResponse | { relatorio_texto?: string }>(
          "/api/grafico",
          {
            method: "POST",
            body: JSON.stringify(payload),
          },
        );
        if ("relatorio_texto" in raw && raw.relatorio_texto) {
          onAnalysisComplete({
            kind: "manual",
            graficos: [],
            relatorio_texto: raw.relatorio_texto,
          });
        } else if ("graficos" in raw && raw.graficos) {
          onAnalysisComplete({
            kind: "manual",
            graficos: raw.graficos,
          });
        } else {
          throw new Error("Resposta inesperada do servidor.");
        }
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Falha ao gerar análise.";
      onError(msg);
      onAnalysisComplete(null);
    } finally {
      onLoading(false);
    }
  }, [
    canGenerate,
    baseFilename,
    guidedId,
    period,
    curso,
    compareFile,
    mainColumn,
    chartType,
    groupBy,
    onAnalysisComplete,
    onLoading,
    onError,
  ]);

  return (
    <section
      className="space-y-8"
      aria-label="Painel de controle — fluxo de análise"
    >
      <div className="flex flex-col items-center gap-6">
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">
          Painel de controle
        </h1>
        <div
          className="flex w-full max-w-3xl items-center justify-between gap-1 px-1 sm:gap-2"
          role="list"
          aria-label="Progresso"
        >
          <StepCircle
            step={1}
            label="Selecionar Dados"
            state={getStepVisual(1)}
          />
          <StepConnector done={step1Done} />
          <StepCircle step={2} label="Configurar" state={getStepVisual(2)} />
          <StepConnector done={configurationComplete} />
          <StepCircle step={3} label="Gerar" state={getStepVisual(3)} />
        </div>
      </div>

      {listError ? (
        <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {listError}
        </p>
      ) : null}

      <div className="grid gap-8 lg:grid-cols-3">
        <Card
          className={cn(
            "shadow-sm transition-all duration-200",
            step1Done &&
              "border-2 border-emerald-500 shadow-md ring-1 ring-emerald-500/20",
          )}
        >
          <CardHeader className="space-y-3 pb-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-semibold text-[#0B3353]">
                  PASSO 1
                </span>
                <Database className="h-4 w-4 shrink-0 text-[#0B3353]" aria-hidden />
              </div>
              {step1Done ? (
                <CheckCircle2
                  className="h-5 w-5 shrink-0 text-emerald-500"
                  aria-label="Passo 1 concluído"
                />
              ) : null}
            </div>
            <CardTitle className="text-base font-semibold">Fonte de Dados</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="origin">Origem</Label>
              <Select
                value={origin}
                onValueChange={(v) => {
                  setOrigin(v as DataOrigin);
                  setBaseFile(undefined);
                }}
              >
                <SelectTrigger
                  id="origin"
                  aria-required
                  className={fieldSuccessClass(!!origin)}
                >
                  <SelectValue placeholder={PLACEHOLDER} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">Arquivos CSV</SelectItem>
                  <SelectItem value="database">Base interna (SQLite)</SelectItem>
                  <SelectItem value="api">API da faculdade</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {origin && origin !== "database" ? (
              <div className="space-y-2">
                <Label htmlFor="base-file">
                  Base de análise <span className="text-red-600">*</span>
                </Label>
                <Select
                  value={baseFile}
                  onValueChange={setBaseFile}
                  disabled={baseOptions.length === 0}
                >
                  <SelectTrigger
                    id="base-file"
                    aria-required
                    className={fieldSuccessClass(!!baseFile)}
                  >
                    <SelectValue placeholder={PLACEHOLDER} />
                  </SelectTrigger>
                  <SelectContent>
                    {baseOptions.map((f) => (
                      <SelectItem key={f} value={f}>
                        {f}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {baseOptions.length === 0 ? (
                  <p className="text-xs text-amber-700">
                    Nenhum arquivo disponível para esta origem. Envie CSV ou
                    inicie a API da faculdade.
                  </p>
                ) : null}
              </div>
            ) : null}

            {origin === "database" ? (
              <p className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
                Será utilizada a base interna{" "}
                <code className="rounded bg-white px-1">__DB_DATA__</code>{" "}
                (mesmo fluxo do painel Flask).
              </p>
            ) : null}

            <div className="space-y-2">
              <Label
                htmlFor="compare"
                className="inline-flex items-center gap-2"
              >
                <GitCompare className="h-4 w-4 text-slate-500" aria-hidden />
                Comparar com (opcional)
              </Label>
              <Select
                value={compareFile ?? COMPARE_NONE}
                onValueChange={setCompareFile}
                disabled={!baseFilename}
              >
                <SelectTrigger id="compare">
                  <SelectValue placeholder={PLACEHOLDER} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={COMPARE_NONE}>(nenhum)</SelectItem>
                  {files.map((f) => (
                    <SelectItem key={f} value={f}>
                      {f}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card
          className={cn(
            "shadow-sm transition-all duration-200",
            !step1Done && "opacity-60",
            configurationComplete &&
              "border-2 border-emerald-500 shadow-md ring-1 ring-emerald-500/20",
          )}
        >
          <CardHeader className="space-y-3 pb-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-semibold text-[#0B3353]">
                  PASSO 2
                </span>
                <Settings className="h-4 w-4 shrink-0 text-[#0B3353]" aria-hidden />
              </div>
              {configurationComplete ? (
                <CheckCircle2
                  className="h-5 w-5 shrink-0 text-emerald-500"
                  aria-label="Configuração concluída"
                />
              ) : null}
            </div>
            <CardTitle className="text-base font-semibold">Configuração</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="guided">Pergunta orientada</Label>
              <Select
                value={guidedId}
                onValueChange={(v) => {
                  setGuidedId(v);
                  setMainColumn(undefined);
                  setChartType(undefined);
                }}
                disabled={!step1Done}
              >
                <SelectTrigger
                  id="guided"
                  aria-required={step1Done}
                  className={fieldSuccessClass(guidedId !== undefined)}
                >
                  <SelectValue
                    placeholder={
                      step1Done ? PLACEHOLDER : "Conclua o Passo 1 primeiro"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={GUIDED_NONE}>
                    — Nenhuma (configurar manualmente) —
                  </SelectItem>
                  {questions.map((q) => (
                    <SelectItem key={q.id} value={q.id}>
                      {q.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {guidedId && guidedId !== GUIDED_NONE && meta ? (
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="period">Período (opcional)</Label>
                  <Select
                    value={period ?? PERIOD_ALL}
                    onValueChange={setPeriod}
                  >
                    <SelectTrigger id="period">
                      <SelectValue placeholder={PLACEHOLDER} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={PERIOD_ALL}>Todos os períodos</SelectItem>
                      {(meta.periods ?? []).map((p) => (
                        <SelectItem key={p} value={p}>
                          {p}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="curso">Curso (opcional)</Label>
                  <Select value={curso ?? CURSO_ALL} onValueChange={setCurso}>
                    <SelectTrigger id="curso">
                      <SelectValue placeholder={PLACEHOLDER} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={CURSO_ALL}>Todos os cursos</SelectItem>
                      {(meta.cursos ?? []).map((c) => (
                        <SelectItem key={c} value={c}>
                          {c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ) : null}

            {needsStep3 ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="col-main">
                    Coluna principal <span className="text-red-600">*</span>
                  </Label>
                  <Select
                    value={mainColumn}
                    onValueChange={setMainColumn}
                    disabled={!baseFilename || columns.length === 0}
                  >
                    <SelectTrigger
                      id="col-main"
                      aria-required
                      className={fieldSuccessClass(!!mainColumn)}
                    >
                      <SelectValue
                        placeholder={
                          baseFilename
                            ? PLACEHOLDER
                            : "Selecione uma base no Passo 1"
                        }
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {columns.map((c) => (
                        <SelectItem key={c.name} value={c.name}>
                          {c.name}
                          {c.is_numeric ? " (numérica)" : ""}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="groupby">Agrupar por (opcional)</Label>
                  <Select
                    value={groupBy ?? GROUP_NONE}
                    onValueChange={setGroupBy}
                  >
                    <SelectTrigger
                      id="groupby"
                      className={fieldSuccessClass(
                        !!groupBy && groupBy !== GROUP_NONE,
                      )}
                    >
                      <SelectValue placeholder={PLACEHOLDER} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={GROUP_NONE}>
                        Nenhum agrupamento
                      </SelectItem>
                      {columns.map((c) => (
                        <SelectItem key={`g-${c.name}`} value={c.name}>
                          {c.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="chart-type">Tipo de visualização</Label>
                  <Select
                    value={chartType}
                    onValueChange={(v) =>
                      setChartType(v as ManualChartType)
                    }
                  >
                    <SelectTrigger
                      id="chart-type"
                      className={cn(
                        "flex w-full items-center gap-2",
                        fieldSuccessClass(!!chartType),
                      )}
                    >
                      {chartType ? (
                        <span className="shrink-0 text-slate-500" aria-hidden>
                          {
                            CHART_OPTIONS.find((o) => o.value === chartType)
                              ?.icon
                          }
                        </span>
                      ) : null}
                      <SelectValue placeholder={PLACEHOLDER} />
                    </SelectTrigger>
                    <SelectContent>
                      {CHART_OPTIONS.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>
                          <span className="flex items-center gap-2">
                            <span className="text-slate-500">{opt.icon}</span>
                            {opt.label}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            ) : null}
          </CardContent>
        </Card>

        <Card className="shadow-sm transition-all duration-200">
          <CardHeader className="space-y-3 pb-4">
            <div className="flex items-center gap-2">
              <Link2 className="h-4 w-4 text-[#0B3353]" aria-hidden />
              <CardTitle className="text-base font-semibold">Informações</CardTitle>
            </div>
            <CardDescription className="text-sm leading-relaxed text-slate-600">
              Configure os dados e clique em &quot;Gerar Análise&quot; para
              visualizar os resultados.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg bg-slate-100 p-4">
              <ul className="space-y-3 text-sm text-slate-700" role="list">
                <li className="flex items-start gap-2">
                  <CheckCircle2
                    className={cn(
                      "mt-0.5 h-4 w-4 shrink-0",
                      step1Done ? "text-emerald-600" : "text-slate-300",
                    )}
                    aria-hidden
                  />
                  <span>Arquivo selecionado</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2
                    className={cn(
                      "mt-0.5 h-4 w-4 shrink-0",
                      (needsStep3
                    ? !!mainColumn
                    : guidedId !== undefined &&
                        guidedId !== GUIDED_NONE)
                        ? "text-emerald-600"
                        : "text-slate-300",
                    )}
                    aria-hidden
                  />
                  <span>Coluna configurada</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2
                    className={cn(
                      "mt-0.5 h-4 w-4 shrink-0",
                      canGenerate ? "text-emerald-600" : "text-slate-300",
                    )}
                    aria-hidden
                  />
                  <span>Pronto para gerar</span>
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-2 grid gap-8 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm lg:col-span-2">
          <button
            type="button"
            className="flex w-full items-center justify-between gap-2 rounded-md px-1 py-1 text-left text-sm font-semibold text-[#0B3353] transition-all duration-200 hover:bg-slate-50"
            onClick={() => setAdvancedOpen((v) => !v)}
            aria-expanded={advancedOpen}
          >
            <span className="inline-flex items-center gap-2">
              <Filter className="h-4 w-4" aria-hidden />
              Filtros avançados
            </span>
            <ChevronDown
              className={cn(
                "h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200",
                advancedOpen && "rotate-180",
              )}
              aria-hidden
            />
          </button>
          {advancedOpen ? (
            <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed text-slate-600">
              Filtros por coluna podem ser integrados ao payload{" "}
              <code className="rounded bg-white px-1">filtros</code> do endpoint{" "}
              <code className="rounded bg-white px-1">/api/grafico</code> numa
              próxima iteração.
            </p>
          ) : null}
        </div>
        <div className="hidden lg:block" aria-hidden />
      </div>

      <div className="flex flex-col gap-4 border-t border-slate-200 bg-white px-4 py-6 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <p className="text-base font-semibold text-slate-900">
            Pronto para visualizar seus dados?
          </p>
          <p className="mt-1 text-sm text-slate-600">{footerSubline}</p>
        </div>
        <Button
          type="button"
          size="lg"
          disabled={!canGenerate}
          onClick={() => void handleGenerate()}
          className="h-12 shrink-0 gap-2 px-8 text-base font-semibold"
        >
          <BarChart3 className="h-5 w-5" aria-hidden />
          Gerar Análise
        </Button>
      </div>
    </section>
  );
}
