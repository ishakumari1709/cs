interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === 'user';

  let isImageMessage = false;
  let imageData: string | null = null;
  let mimeType: string = 'image/jpeg';
  let textContent = content;

  try {
    const parsed = JSON.parse(content);
    if (parsed.type === 'image' && parsed.data) {
      isImageMessage = true;
      imageData = parsed.data;
      mimeType = parsed.mimeType || 'image/jpeg';
    }
  } catch (e) {
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div
        className={`max-w-[75%] rounded-3xl transition-all duration-300 transform hover:scale-105 ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-sm shadow-lg'
            : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-900 rounded-bl-sm shadow-md'
        }`}
      >
        {isImageMessage && imageData ? (
          <img
            src={imageData}
            alt="User uploaded"
            className="rounded-3xl rounded-br-sm max-h-80 w-auto object-cover shadow-inner"
          />
        ) : (
          <p className="px-5 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words font-medium">
            {textContent}
          </p>
        )}
      </div>
    </div>
  );
}
