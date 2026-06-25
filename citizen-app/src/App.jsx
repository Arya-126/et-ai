import { useState, useRef, useEffect } from "react";
import { submitReport } from "./api.js";
import ChatBubble from "./components/ChatBubble.jsx";
import Verdict from "./components/Verdict.jsx";

const EXAMPLES = [
  {
    label: "📞 CBI 'digital arrest'",
    text:
      "This is Inspector Sharma from CBI. Your Aadhaar is linked to a money laundering case. " +
      "You are under digital arrest — stay on this video call and do not disconnect or tell anyone. " +
      "Transfer a refundable security deposit to digitalarrest.a@okaxis to clear your name. Call back +919876543210.",
  },
  {
    label: "📦 Customs parcel",
    text:
      "Customs Department: a parcel in your name with illegal drugs was seized. Pay a verification fee " +
      "to parcelscam.b@okaxis immediately or face arrest.",
  },
  { label: "💬 Benign message", text: "Mom, dinner at 8? I'll bring dessert." },
];

export default function App() {
  const [messages, setMessages] = useState([
    { kind: "verdict", report: { verdict: "LIKELY SAFE", advice: "Hi! Paste any suspicious call, SMS or message you received and I'll tell you in seconds whether it's a scam. I never ask for your OTP or money.", red_flags: [] } },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, busy]);

  async function send(text) {
    const t = (text ?? input).trim();
    if (!t || busy) return;
    setInput("");
    setMessages((m) => [...m, { kind: "user", text: t }]);
    setBusy(true);
    try {
      const report = await submitReport(t);
      setMessages((m) => [...m, { kind: "verdict", report }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { kind: "verdict", report: { verdict: "SUSPICIOUS", advice: "Couldn't reach Fraud Shield backend. Is the API running on :8000?", red_flags: [] } },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-200 p-4">
      <div className="w-full max-w-md h-[90vh] flex flex-col rounded-xl overflow-hidden shadow-2xl bg-white">
        {/* header */}
        <div className="bg-[#075e54] text-white px-4 py-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-400 flex items-center justify-center text-xl">🛡️</div>
          <div>
            <div className="font-semibold leading-tight">Fraud Shield</div>
            <div className="text-xs text-emerald-100">online · protecting you</div>
          </div>
        </div>

        {/* chat */}
        <div className="flex-1 overflow-y-auto chat-bg px-3 py-4 space-y-3">
          {messages.map((m, i) =>
            m.kind === "user" ? <ChatBubble key={i} text={m.text} /> : <Verdict key={i} report={m.report} />
          )}
          {busy && <div className="text-xs text-gray-500 pl-2">Fraud Shield is analysing…</div>}
          <div ref={endRef} />
        </div>

        {/* quick examples */}
        <div className="flex gap-2 px-3 py-2 bg-gray-50 overflow-x-auto">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => send(ex.text)}
              disabled={busy}
              className="whitespace-nowrap text-xs bg-white border border-gray-200 rounded-full px-3 py-1 hover:bg-gray-100 disabled:opacity-50"
            >
              {ex.label}
            </button>
          ))}
        </div>

        {/* input */}
        <div className="flex items-center gap-2 p-3 bg-gray-100">
          <textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Paste a suspicious message…"
            className="flex-1 resize-none rounded-full px-4 py-2 text-sm outline-none border border-gray-200"
          />
          <button
            onClick={() => send()}
            disabled={busy}
            className="w-10 h-10 rounded-full bg-[#075e54] text-white flex items-center justify-center disabled:opacity-50"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
