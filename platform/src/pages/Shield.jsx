import { useState, useRef, useEffect } from "react";
import { submitReport, fetchLanguages } from "../api.js";
import { ui } from "../i18n.js";
import ChatBubble from "../components/chat/ChatBubble.jsx";
import Verdict from "../components/chat/Verdict.jsx";

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

export default function Shield() {
  const [messages, setMessages] = useState([
    { kind: "verdict", report: { verdict: "LIKELY SAFE", advice: "Hi! Paste any suspicious call, SMS or message you received and I'll tell you in seconds whether it's a scam. I never ask for your OTP or money.", red_flags: [] } },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [lang, setLang] = useState("en");
  const [langs, setLangs] = useState({ en: "English" });
  const [channel, setChannel] = useState("whatsapp");   // whatsapp | ivr
  const endRef = useRef(null);

  useEffect(() => { fetchLanguages().then(setLangs).catch(() => {}); }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, busy]);

  async function send(text) {
    const t = (text ?? input).trim();
    if (!t || busy) return;
    setInput("");
    setMessages((m) => [...m, { kind: "user", text: t }]);
    setBusy(true);
    try {
      const report = await submitReport(t, channel, lang);
      setMessages((m) => [...m, { kind: "verdict", report, lang }]);
    } catch (e) {
      setMessages((m) => [...m, { kind: "verdict", report: { verdict: "SUSPICIOUS", advice: "Couldn't reach the Fraud Shield backend. Is the API running on :8000?", red_flags: [] }, lang }]);
    } finally {
      setBusy(false);
    }
  }

  const ivr = channel === "ivr";

  return (
    <div className="h-full flex items-center justify-center bg-slate-200 p-4">
      <div className="w-full max-w-md h-[88vh] flex flex-col rounded-xl overflow-hidden shadow-2xl bg-white">
        {/* header */}
        <div className={`px-4 py-3 flex items-center gap-3 text-white ${ivr ? "bg-indigo-800" : "bg-[#075e54]"}`}>
          <div className="w-10 h-10 rounded-full bg-emerald-400 flex items-center justify-center text-xl">{ivr ? "☎️" : "🛡️"}</div>
          <div className="flex-1">
            <div className="font-semibold leading-tight">Fraud Shield</div>
            <div className="text-xs text-emerald-100">{ivr ? "IVR helpline · 1930" : "WhatsApp · online"}</div>
          </div>
          {/* language + channel selectors */}
          <select value={lang} onChange={(e) => setLang(e.target.value)}
                  className="text-xs text-slate-800 rounded px-1 py-1 max-w-[7.5rem]">
            {Object.entries(langs).map(([code, name]) => <option key={code} value={code}>{name}</option>)}
          </select>
        </div>

        {/* channel toggle */}
        <div className="flex text-xs border-b border-gray-200">
          {[["whatsapp", "WhatsApp"], ["ivr", "IVR / Call"]].map(([c, lbl]) => (
            <button key={c} onClick={() => setChannel(c)}
                    className={`flex-1 py-1.5 font-medium ${channel === c ? "bg-gray-100 text-slate-900" : "text-slate-400"}`}>
              {lbl}
            </button>
          ))}
        </div>

        {/* chat */}
        <div className="flex-1 overflow-y-auto chat-bg px-3 py-4 space-y-3">
          {ivr && (
            <div className="text-xs text-indigo-700 bg-indigo-50 rounded-lg p-2">
              ☎️ IVR mode: "Welcome to 1930. Describe the call or message you received after the beep."
              (Same AI backend as WhatsApp — multi-channel.)
            </div>
          )}
          {messages.map((m, i) =>
            m.kind === "user" ? <ChatBubble key={i} text={m.text} /> : <Verdict key={i} report={m.report} lang={m.lang || "en"} />
          )}
          {busy && <div className="text-xs text-gray-500 pl-2">Fraud Shield is analysing…</div>}
          <div ref={endRef} />
        </div>

        {/* quick examples (IVR shows them as DTMF prompts) */}
        <div className="flex gap-2 px-3 py-2 bg-gray-50 overflow-x-auto">
          {EXAMPLES.map((ex, i) => (
            <button key={i} onClick={() => send(ex.text)} disabled={busy}
                    className="whitespace-nowrap text-xs bg-white border border-gray-200 rounded-full px-3 py-1 hover:bg-gray-100 disabled:opacity-50">
              {ivr ? `Press ${i + 1} · ` : ""}{ex.label}
            </button>
          ))}
        </div>

        {/* input */}
        <div className="flex items-center gap-2 p-3 bg-gray-100">
          <textarea rows={1} value={input} onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
                    placeholder={ui("placeholder", lang)}
                    className="flex-1 resize-none rounded-full px-4 py-2 text-sm outline-none border border-gray-200" />
          <button onClick={() => send()} disabled={busy}
                  className={`w-10 h-10 rounded-full text-white flex items-center justify-center disabled:opacity-50 ${ivr ? "bg-indigo-800" : "bg-[#075e54]"}`}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
