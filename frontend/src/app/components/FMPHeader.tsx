import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import { Button } from "@/app/components/ui/button";
import { cn } from "@/lib/utils";
import { BarChart3, ChevronDown, LogOut, Menu, Settings, User, X } from "lucide-react";

const NAV = [
  { href: "#dashboard", label: "Dashboard" },
  { href: "#analises", label: "Análises" },
  { href: "#relatorios", label: "Relatórios" },
  { href: "#configuracoes", label: "Configurações" },
] as const;

type FMPHeaderProps = {
  /** GitHub Pages: volta à tela de login (sessão apenas no navegador). */
  onLogout?: () => void;
};

export function FMPHeader({ onLogout }: FMPHeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [logoOk, setLogoOk] = useState(true);

  return (
    <header
      className={cn(
        "w-full bg-gradient-to-r from-[#0B3353] to-[#09283f] text-white shadow-md transition-all duration-200",
      )}
      role="banner"
    >
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex min-w-0 flex-1 items-center gap-3">
          <a
            href={import.meta.env.BASE_URL}
            className="flex shrink-0 items-center gap-2 rounded-lg outline-none ring-offset-2 focus-visible:ring-2 focus-visible:ring-sky-300"
            aria-label="Faculdade Maria da Penha — início"
          >
            {logoOk ? (
              <img
                src={`${import.meta.env.BASE_URL}logo-sem-fundo.png`}
                alt=""
                className="h-9 w-auto max-w-[140px] object-contain"
                width={140}
                height={36}
                onError={() => setLogoOk(false)}
              />
            ) : (
              <span className="flex h-9 items-center rounded-md border border-white/20 bg-white/10 px-3 text-sm font-semibold tracking-tight">
                FMP
              </span>
            )}
          </a>
        </div>

        <nav
          className="hidden flex-1 justify-center md:flex"
          aria-label="Principal"
        >
          <ul className="flex flex-wrap items-center justify-center gap-1 lg:gap-2">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-white/90 transition-all duration-200 hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-300"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                type="button"
                variant="outline"
                className="h-10 gap-2 border-white/30 bg-white/10 px-3 text-white hover:bg-white/15"
                aria-label="Menu do usuário"
              >
                <span
                  className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-white/20 ring-2 ring-white/30"
                  aria-hidden
                >
                  <User className="h-4 w-4" />
                </span>
                <span className="hidden max-w-[10rem] truncate text-sm font-medium sm:inline">
                  Coordenador
                </span>
                <ChevronDown className="hidden h-4 w-4 opacity-80 sm:inline" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-56 border-slate-200 bg-white text-slate-900"
              align="end"
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">Coordenador</p>
                  <p className="text-xs text-slate-500">Painel de análises</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Settings className="h-4 w-4" />
                Preferências
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer gap-2 text-red-600 focus:text-red-600"
                onClick={() => onLogout?.()}
              >
                <LogOut className="h-4 w-4" />
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            type="button"
            variant="ghost"
            className="h-10 w-10 shrink-0 text-white hover:bg-white/10 md:hidden"
            aria-expanded={mobileOpen}
            aria-controls="mobile-nav"
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
            <span className="sr-only">
              {mobileOpen ? "Fechar menu" : "Abrir menu"}
            </span>
          </Button>
        </div>
      </div>

      {mobileOpen ? (
        <div
          id="mobile-nav"
          className="border-t border-white/10 px-4 py-4 md:hidden"
        >
          <ul className="flex flex-col gap-1">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="flex items-center gap-2 rounded-lg px-3 py-3 text-sm font-medium text-white/95 hover:bg-white/10"
                  onClick={() => setMobileOpen(false)}
                >
                  <BarChart3 className="h-4 w-4 opacity-80" aria-hidden />
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </header>
  );
}
