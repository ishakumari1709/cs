import { FileText, Upload } from 'lucide-react';

interface UploadSectionProps {
  onDocumentUpload: (file: File) => void;
  onScreenshotUpload: (file: File) => void;
}

export default function UploadSection({ onDocumentUpload, onScreenshotUpload }: UploadSectionProps) {
  const handleDocumentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onDocumentUpload(file);
      e.target.value = '';
    }
  };

  const handleScreenshotChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onScreenshotUpload(file);
      e.target.value = '';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <label className="flex-1 max-w-xs group">
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleDocumentChange}
            className="hidden"
          />
          <div className="flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-200 rounded-2xl cursor-pointer transition-all duration-300 hover:border-blue-500 hover:shadow-xl hover:bg-blue-50 group-hover:scale-105 transform">
            <div className="p-2 bg-gradient-to-br from-blue-100 to-blue-50 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div className="text-left">
              <span className="font-semibold text-gray-900 block">Upload Document</span>
              <span className="text-xs text-gray-500">PDF, DOCX files</span>
            </div>
          </div>
        </label>

        <label className="flex-1 max-w-xs group">
          <input
            type="file"
            accept="image/*"
            onChange={handleScreenshotChange}
            className="hidden"
          />
          <div className="flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-200 rounded-2xl cursor-pointer transition-all duration-300 hover:border-blue-500 hover:shadow-xl hover:bg-blue-50 group-hover:scale-105 transform">
            <div className="p-2 bg-gradient-to-br from-blue-100 to-blue-50 rounded-lg">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
            <div className="text-left">
              <span className="font-semibold text-gray-900 block">Upload Screenshot</span>
              <span className="text-xs text-gray-500">Image files</span>
            </div>
          </div>
        </label>
      </div>
    </div>
  );
}
