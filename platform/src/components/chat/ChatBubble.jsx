export default function ChatBubble({ text }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-[#d9fdd3] shadow px-4 py-2 text-sm text-gray-800 whitespace-pre-wrap">
        {text}
      </div>
    </div>
  );
}
