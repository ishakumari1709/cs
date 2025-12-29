import { useEffect } from 'react';
import { CheckCircle } from 'lucide-react';

interface NotificationProps {
  message: string;
  onClose: () => void;
}

export default function Notification({ message, onClose }: NotificationProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-24 right-6 z-50 animate-slide-in">
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl shadow-xl px-6 py-4 flex items-center gap-3 min-w-[280px] backdrop-blur-sm">
        <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
        <p className="text-sm text-gray-800 font-semibold">{message}</p>
      </div>
    </div>
  );
}
