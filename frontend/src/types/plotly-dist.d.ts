declare module "plotly.js-dist-min" {
  interface PlotlyStatic {
    newPlot: (
      root: HTMLElement,
      data: object[],
      layout?: Record<string, unknown>,
      config?: Record<string, unknown>,
    ) => Promise<void>;
    purge: (root: HTMLElement) => void;
    relayout: (
      root: HTMLElement,
      update: Record<string, unknown>,
    ) => Promise<unknown>;
  }
  const Plotly: PlotlyStatic;
  export default Plotly;
}
