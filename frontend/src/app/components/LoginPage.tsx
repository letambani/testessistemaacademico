import { useId, useState } from "react";
import { Button } from "@/app/components/ui/button";
import { cn } from "@/lib/utils";
import { Eye, EyeOff } from "lucide-react";

type Props = {
  onSuccess: () => void;
};

const base = import.meta.env.BASE_URL;

export function LoginPage({ onSuccess }: Props) {
  const emailId = useId();
  const pwdId = useId();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const em = email.trim();
    if (!em || !password) {
      setError("Preencha e-mail e senha.");
      return;
    }
    sessionStorage.setItem("fmp_gh_pages_auth", "1");
    onSuccess();
  }

  return (
    <div
      className={cn(
        "flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-8",
        "bg-gradient-to-b from-white to-slate-50 text-[#0B3353]",
      )}
    >
      <div className="flex w-full max-w-[1100px] flex-col items-center gap-8">
        <header className="flex flex-col items-center gap-2 text-center">
          <img
            src={`${base}logo.png`}
            alt="Logo FMP — Faculdade Municipal de Palhoça"
            className="h-auto w-[min(260px,85vw)] object-contain"
            width={260}
            height={120}
          />
          <div>
            <p className="text-lg font-bold tracking-tight">FMP</p>
            <p className="text-sm text-[#0B3353]/80">
              Faculdade Municipal de Palhoça
            </p>
          </div>
        </header>

        <section
          className="w-full max-w-[360px] rounded-[14px] border border-[#0B3353]/10 bg-white p-6 shadow-[0_10px_30px_rgba(11,51,83,0.08)]"
          aria-labelledby="login-heading"
        >
          <h1 id="login-heading" className="mb-3 text-[22px] font-semibold">
            Login
          </h1>

          <p className="mb-4 text-xs leading-relaxed text-slate-600">
            No site estático (GitHub Pages) o acesso é demonstrativo: após
            entrar, a interface carrega sem validação no servidor. O login real
            com banco de dados ocorre ao rodar o backend Flask localmente.
          </p>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label
                htmlFor={emailId}
                className="mb-1.5 block text-[13px] font-semibold"
              >
                E-mail
              </label>
              <input
                id={emailId}
                name="email"
                type="email"
                autoComplete="email"
                placeholder="seu@exemplo.com"
                value={email}
                onChange={(ev) => setEmail(ev.target.value)}
                className="w-full rounded-[10px] border-[1.5px] border-[#0B3353]/15 bg-white px-3.5 py-3 text-sm outline-none transition focus:border-[#0B3353] focus:shadow-[0_6px_20px_rgba(11,51,83,0.06)]"
              />
            </div>

            <div>
              <label
                htmlFor={pwdId}
                className="mb-1.5 block text-[13px] font-semibold"
              >
                Senha
              </label>
              <div className="relative">
                <input
                  id={pwdId}
                  name="password"
                  type={showPwd ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="Digite sua senha"
                  value={password}
                  onChange={(ev) => setPassword(ev.target.value)}
                  className="w-full rounded-[10px] border-[1.5px] border-[#0B3353]/15 bg-white px-3.5 py-3 pr-11 text-sm outline-none transition focus:border-[#0B3353] focus:shadow-[0_6px_20px_rgba(11,51,83,0.06)]"
                />
                <button
                  type="button"
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-[#0B3353] hover:bg-slate-100"
                  onClick={() => setShowPwd((v) => !v)}
                  aria-label={showPwd ? "Ocultar senha" : "Mostrar senha"}
                >
                  {showPwd ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {error ? (
              <p className="text-sm text-red-600" role="alert">
                {error}
              </p>
            ) : null}

            <div className="flex flex-wrap gap-2 pt-1">
              <Button
                type="submit"
                className="bg-[#0B3353] hover:bg-[#09283f]"
              >
                Entrar
              </Button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
