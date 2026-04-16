import { useId, useState } from "react";
import "@/styles/login-template.css";

const base = import.meta.env.BASE_URL;

type Props = {
  onSuccess: () => void;
};

export function LoginPage({ onSuccess }: Props) {
  const emailId = useId();
  const pwdId = useId();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const togglePwdLabel = showPwd ? "Ocultar" : "Mostrar";

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
    <div className="login-template-root">
      <main className="center-wrap" role="main">
        <section className="logo">
          <img
            src={`${base}logo.png`}
            alt="Logo FMP — Faculdade Municipal de Palhoça"
          />
          <div className="brand-sub">
            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--azul)" }}>
              FMP
            </div>
            <div
              style={{
                fontSize: 13,
                color: "rgba(11,51,83,0.8)",
                marginTop: 2,
              }}
            >
              Faculdade Municipal de Palhoça
            </div>
          </div>
        </section>

        <section className="login-card">
          <h2>Login</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor={emailId}>E-mail</label>
              <input
                id={emailId}
                name="email"
                type="email"
                value={email}
                onChange={(ev) => setEmail(ev.target.value)}
                placeholder="seu@exemplo.com"
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor={pwdId}>Senha</label>
              <div style={{ position: "relative" }}>
                <input
                  id={pwdId}
                  className="senha-field"
                  name="senha"
                  type={showPwd ? "text" : "password"}
                  value={password}
                  onChange={(ev) => setPassword(ev.target.value)}
                  placeholder="Digite sua senha"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  id="togglePwd"
                  onClick={() => setShowPwd((v) => !v)}
                  style={{
                    position: "absolute",
                    right: 8,
                    top: 6,
                    height: 32,
                    padding: "6px 8px",
                    borderRadius: 8,
                    border: 0,
                    background: "transparent",
                    cursor: "pointer",
                    color: "var(--azul)",
                    fontWeight: 700,
                  }}
                >
                  {togglePwdLabel}
                </button>
              </div>
            </div>

            <div className="row-between" style={{ marginBottom: 12 }}>
              <div />
              <a
                href="#"
                className="forgot"
                onClick={(ev) => ev.preventDefault()}
                title="Disponível com o servidor Flask (recuperar senha)"
              >
                Esqueci a senha
              </a>
            </div>

            {error ? (
              <ul
                style={{
                  marginTop: 10,
                  listStyle: "none",
                  padding: 0,
                }}
              >
                <li style={{ color: "#c00", fontSize: 14 }}>{error}</li>
              </ul>
            ) : null}

            <div>
              <button className="btn btn-primary" type="submit">
                Entrar
              </button>
              <a
                href="#"
                className="btn btn-outline"
                role="button"
                onClick={(ev) => ev.preventDefault()}
                title="Disponível com o servidor Flask (cadastro)"
              >
                Cadastrar
              </a>
            </div>

            <div className="small-note" style={{ marginTop: 12 }}>
              Não possui conta? Clique em <strong>Cadastrar</strong>.
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}
