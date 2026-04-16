import { useState } from "react";
import { Button } from "@/app/components/ui/button";
import { MessageCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function Chatbot() {
  const [open, setOpen] = useState(false);

  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3 sm:bottom-8 sm:right-8">
      {open ? (
        <div
          id="chatbot-panel"
          className="pointer-events-auto w-[min(100vw-2rem,22rem)] rounded-lg border border-slate-200 bg-white p-4 shadow-lg transition-all duration-200"
          role="dialog"
          aria-label="Assistente"
        >
          <div className="mb-3 flex items-center justify-between gap-2">
            <p className="text-sm font-semibold text-slate-900">Assistente</p>
            <Button
              type="button"
              variant="secondary"
              size="icon"
              className="h-8 w-8 shrink-0"
              onClick={() => setOpen(false)}
              aria-label="Fechar assistente"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs leading-relaxed text-slate-600">
            O chat com IA pode ser integrado ao endpoint{" "}
            <code className="rounded bg-slate-100 px-1 py-0.5 text-[0.7rem]">
              /api/chat
            </code>{" "}
            do backend Flask quando a sessão estiver ativa.
          </p>
        </div>
      ) : null}
      <Button
        type="button"
        size="lg"
        className={cn(
          "pointer-events-auto h-14 w-14 rounded-full p-0 shadow-lg transition-all duration-200",
        )}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="chatbot-panel"
        id="chatbot-toggle"
      >
        {open ? (
          <X className="h-6 w-6" aria-hidden />
        ) : (
          <MessageCircle className="h-6 w-6" aria-hidden />
        )}
        <span className="sr-only">
          {open ? "Fechar assistente" : "Abrir assistente"}
        </span>
      </Button>
    </div>
  );
}
