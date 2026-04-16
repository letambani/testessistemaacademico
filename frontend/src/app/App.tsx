import { useState } from "react";
import { Chatbot } from "@/app/components/Chatbot";
import { ControlPanel } from "@/app/components/ControlPanel";
import { FMPFooter } from "@/app/components/FMPFooter";
import { FMPHeader } from "@/app/components/FMPHeader";
import { ResultsPanel } from "@/app/components/ResultsPanel";
import type { AnalysisResult } from "@/types/analysis";

export default function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="flex min-h-screen flex-col">
      <FMPHeader />
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
