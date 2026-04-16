export function FMPFooter() {
  const year = new Date().getFullYear();
  return (
    <footer
      className="mt-auto border-t border-slate-200 bg-white py-8 text-center text-sm text-slate-600 shadow-sm transition-all duration-200"
      role="contentinfo"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p>
          © {year} Faculdade Maria da Penha — Todos os direitos reservados.
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Painel institucional de análise de dados educacionais.
        </p>
      </div>
    </footer>
  );
}
