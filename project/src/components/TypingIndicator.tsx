export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 animate-fade-in">
      <div className="bg-gradient-to-br from-gray-100 to-gray-200 px-5 py-3 rounded-3xl rounded-bl-sm shadow-md">
        <div className="flex gap-2">
          <div className="w-3 h-3 bg-gradient-to-b from-gray-400 to-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-3 h-3 bg-gradient-to-b from-gray-400 to-gray-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-3 h-3 bg-gradient-to-b from-gray-400 to-gray-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}
