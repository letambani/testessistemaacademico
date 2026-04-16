import { useEffect, useRef } from "react";
import type { PlotlyFigure } from "@/types/analysis";
import { cn } from "@/lib/utils";

type PlotlyStatic = {
  newPlot: (
    el: HTMLElement,
    data: object[],
    layout?: Record<string, unknown>,
    config?: Record<string, unknown>,
  ) => Promise<void>;
  purge: (el: HTMLElement) => void;
  relayout: (
    el: HTMLElement,
    update: Record<string, unknown>,
  ) => Promise<void>;
};

let plotlyPromise: Promise<PlotlyStatic> | null = null;

function loadPlotly(): Promise<PlotlyStatic> {
  if (!plotlyPromise) {
    plotlyPromise = import("plotly.js-dist-min").then((m) => {
      const mod = m as { default?: PlotlyStatic } & PlotlyStatic;
      return (mod.default ?? mod) as PlotlyStatic;
    });
  }
  return plotlyPromise;
}

interface PlotlyChartProps {
  figure: PlotlyFigure;
  className?: string;
  title?: string;
}

export function PlotlyChart({ figure, className, title }: PlotlyChartProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    let cancelled = false;
    let Plotly: PlotlyStatic | null = null;

    void (async () => {
      Plotly = await loadPlotly();
      if (cancelled || !ref.current) return;
      await Plotly.newPlot(
        ref.current,
        figure.data,
        {
          ...figure.layout,
          autosize: true,
        },
        {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
        },
      );
    })();

    const onResize = () => {
      if (!ref.current || !Plotly) return;
      void Plotly.relayout(ref.current, {
        width: ref.current.clientWidth,
      });
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelled = true;
      window.removeEventListener("resize", onResize);
      void loadPlotly().then((P) => {
        if (ref.current) P.purge(ref.current);
      });
    };
  }, [figure]);

  return (
    <div className={cn("w-full", className)}>
      {title ? (
        <p className="mb-2 text-sm font-medium text-slate-800">{title}</p>
      ) : null}
      <div
        ref={ref}
        className="min-h-[320px] w-full overflow-hidden rounded-lg border border-slate-100 bg-white"
        role="img"
        aria-label={title ?? "Gráfico interativo"}
      />
    </div>
  );
}
