// Client-side localization for verdict labels + a few UI strings. Advice text
// itself comes already-localized from the backend (data/i18n.py).

export const VERDICT_LABEL = {
  "HIGH RISK": {
    en: "HIGH RISK", hi: "अत्यधिक जोखिम", bn: "উচ্চ ঝুঁকি", te: "అధిక ప్రమాదం",
    mr: "उच्च धोका", ta: "அதிக ஆபத்து", gu: "ઉચ્ચ જોખમ", kn: "ಹೆಚ್ಚಿನ ಅಪಾಯ",
    ml: "ഉയർന്ന അപകടം", pa: "ਉੱਚ ਖਤਰਾ", or: "ଉଚ୍ଚ ବିପଦ", as: "উচ্চ বিপদ", ur: "زیادہ خطرہ",
  },
  SUSPICIOUS: {
    en: "SUSPICIOUS", hi: "संदिग्ध", bn: "সন্দেহজনক", te: "అనుమానాస్పదం",
    mr: "संशयास्पद", ta: "சந்தேகம்", gu: "શંકાસ્પદ", kn: "ಸಂಶಯಾಸ್ಪದ",
    ml: "സംശയാസ്പദം", pa: "ਸ਼ੱਕੀ", or: "ସନ୍ଦେହଜନକ", as: "সন্দেহজনক", ur: "مشکوک",
  },
  "LIKELY SAFE": {
    en: "LIKELY SAFE", hi: "संभवतः सुरक्षित", bn: "সম্ভবত নিরাপদ", te: "సురక్షితం",
    mr: "सुरक्षित", ta: "பாதுகாப்பானது", gu: "સલામત", kn: "ಸುರಕ್ಷಿತ",
    ml: "സുരക്ഷിതം", pa: "ਸੁਰੱਖਿਅਤ", or: "ନିରାପଦ", as: "নিৰাপদ", ur: "محفوظ",
  },
};

export const UI = {
  report_cta: {
    en: "Report now — call 1930", hi: "अभी रिपोर्ट करें — 1930", bn: "এখনই রিপোর্ট করুন — 1930",
    ta: "இப்போது புகார் — 1930", te: "ఇప్పుడే ఫిర్యాదు — 1930", default: "Report now — call 1930",
  },
  placeholder: {
    en: "Paste a suspicious message…", hi: "संदिग्ध संदेश पेस्ट करें…",
    ta: "சந்தேக செய்தியை ஒட்டவும்…", default: "Paste a suspicious message…",
  },
  file_complaint: {
    en: "File complaint (1930 / cybercrime.gov.in)", hi: "शिकायत दर्ज करें (1930)",
    default: "File complaint (1930 / cybercrime.gov.in)",
  },
};

export function verdictLabel(verdict, lang) {
  return VERDICT_LABEL[verdict]?.[lang] || verdict;
}

export function ui(key, lang) {
  const t = UI[key] || {};
  return t[lang] || t.default || t.en || key;
}
