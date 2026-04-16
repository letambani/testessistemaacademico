import { useState } from "react";
import { Chatbot } from "@/app/components/Chatbot";
import { ControlPanel } from "@/app/components/ControlPanel";
import { FMPFooter } from "@/app/components/FMPFooter";
import { FMPHeader } from "@/app/components/FMPHeader";
import { LoginPage } from "@/app/components/LoginPage";
import { ResultsPanel } from "@/app/components/ResultsPanel";
import type { AnalysisResult } from "@/types/analysis";

const AUTH_KEY = "fmp_gh_pages_auth";

function readSession(): boolean {
  try {
    return sessionStorage.getItem(AUTH_KEY) === "1";
  } catch {
    return false;
  }
}

export default function App() {
  const [authed, setAuthed] = useState(readSession);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleLogout() {
    try {
      sessionStorage.removeItem(AUTH_KEY);
    } catch {
      /* ignore */
    }
    setAuthed(false);
  }

  if (!authed) {
    return <LoginPage onSuccess={() => setAuthed(true)} />;
  }

  return (
    <div className="flex min-h-screen flex-col">
      <FMPHeader onLogout={handleLogout} />
      <main className="flex flex-1 flex-col">
        <div className="flex-1 px-4 py-8 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <ControlPanel
              onAnalysisComplete={setResult}
              onLoading={setLoading}
              onError={setError}
            />
            <ResultsPanel result={result} loading={loading} error={error} />
          </div>
        </div>
      </main>
      <FMPFooter />
      <Chatbot />
    </div>
  );
}
