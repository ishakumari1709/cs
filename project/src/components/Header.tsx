import { MessageCircle } from 'lucide-react';

export default function Header() {
  return (
    <header className="w-full bg-gradient-to-r from-blue-600 via-blue-500 to-blue-400 py-8 shadow-xl relative overflow-hidden">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-2 left-10 w-24 h-24 bg-white rounded-full blur-2xl"></div>
        <div className="absolute bottom-2 right-20 w-32 h-32 bg-white rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center gap-3">
        <div className="bg-white bg-opacity-20 p-3 rounded-xl backdrop-blur-sm">
          <MessageCircle className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-white text-3xl font-bold tracking-tight">
            AI Customer Support
          </h1>
          <p className="text-blue-100 text-sm font-medium mt-1">Instant assistance, always available</p>
        </div>
      </div>
    </header>
  );
}
