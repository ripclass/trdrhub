import React, { useState } from 'react';
import { ArrowLeft, FileText, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import FileUploader from '../components/FileUploader';

interface UploadProgress {
  fileId: string;
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

const UploadPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFilesSelect = (files: File[]) => {
    setSelectedFiles(files);
  };

  const simulateUploadProgress = (fileId: string, fileName: string) => {
    let progress = 0;

    const updateProgress = () => {
      progress += Math.random() * 15 + 5;

      if (progress >= 100) {
        setUploadProgress(prev =>
          prev.map(p => p.fileId === fileId
            ? { ...p, progress: 100, status: 'processing' as const }
            : p
          )
        );

        setTimeout(() => {
          setUploadProgress(prev =>
            prev.map(p => p.fileId === fileId
              ? { ...p, status: 'completed' as const }
              : p
            )
          );
        }, 2000);

        return;
      }

      setUploadProgress(prev =>
        prev.map(p => p.fileId === fileId
          ? { ...p, progress: Math.floor(progress) }
          : p
        )
      );

      setTimeout(updateProgress, 200 + Math.random() * 300);
    };

    updateProgress();
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);

    const initialProgress: UploadProgress[] = selectedFiles.map(file => ({
      fileId: `${file.name}-${Date.now()}`,
      fileName: file.name,
      progress: 0,
      status: 'uploading' as const,
    }));

    setUploadProgress(initialProgress);

    initialProgress.forEach(progress => {
      simulateUploadProgress(progress.fileId, progress.fileName);
    });

    setTimeout(() => {
      setIsUploading(false);
    }, 8000);
  };

  const handleReset = () => {
    setSelectedFiles([]);
    setUploadProgress([]);
    setIsUploading(false);
  };

  const getProgressIcon = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
        return <Clock size={16} className="text-blue-500 animate-pulse" />;
      case 'processing':
        return <Clock size={16} className="text-yellow-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'error':
        return <AlertCircle size={16} className="text-red-500" />;
    }
  };

  const getProgressText = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
        return 'Uploading...';
      case 'processing':
        return 'Processing...';
      case 'completed':
        return 'Complete';
      case 'error':
        return 'Error';
    }
  };

  const isAllCompleted = uploadProgress.length > 0 &&
    uploadProgress.every(p => p.status === 'completed' || p.status === 'error');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
          <p className="text-gray-600 mt-1">
            Upload your LC documents for analysis and risk assessment
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Select Documents
              </h2>

              <FileUploader
                onFilesSelect={handleFilesSelect}
                maxFiles={5}
                maxSize={10 * 1024 * 1024}
                acceptedTypes={['.pdf', '.jpg', '.jpeg', '.png', '.json']}
                disabled={isUploading}
              />

              {selectedFiles.length > 0 && !isUploading && uploadProgress.length === 0 && (
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleStartUpload}
                    className="btn-primary flex-1"
                  >
                    <FileText size={18} className="mr-2" />
                    Start Analysis ({selectedFiles.length} files)
                  </button>
                  <button
                    onClick={handleReset}
                    className="btn-secondary"
                  >
                    Clear
                  </button>
                </div>
              )}

              {isAllCompleted && (
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={() => window.location.href = '/risk-analysis'}
                    className="btn-primary flex-1"
                  >
                    View Risk Analysis
                  </button>
                  <button
                    onClick={handleReset}
                    className="btn-secondary"
                  >
                    Upload More
                  </button>
                </div>
              )}
            </div>

            {/* Instructions */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Document Requirements
              </h3>

              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>PDF format for LC documents is preferred</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Images (JPG, PNG) supported for certificates and invoices</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Maximum file size: 10MB per document</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Up to 5 documents can be processed simultaneously</span>
                </div>
              </div>

              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">
                  Supported Document Types:
                </h4>
                <div className="text-sm text-blue-800">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Letters of Credit (LC)</li>
                    <li>Commercial Invoices</li>
                    <li>Bills of Lading</li>
                    <li>Certificates of Origin</li>
                    <li>Insurance Documents</li>
                    <li>Packing Lists</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Section */}
          <div className="space-y-6">
            {uploadProgress.length > 0 && (
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Upload Progress
                </h2>

                <div className="space-y-4">
                  {uploadProgress.map((progress) => (
                    <div key={progress.fileId} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          {getProgressIcon(progress.status)}
                          <span className="text-sm font-medium text-gray-900 truncate">
                            {progress.fileName}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span>{getProgressText(progress.status)}</span>
                          {progress.status === 'uploading' && (
                            <span>{progress.progress}%</span>
                          )}
                        </div>
                      </div>

                      {(progress.status === 'uploading' || progress.status === 'processing') && (
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${
                              progress.status === 'uploading'
                                ? 'bg-blue-500'
                                : 'bg-yellow-500'
                            }`}
                            style={{
                              width: progress.status === 'uploading'
                                ? `${progress.progress}%`
                                : '100%'
                            }}
                          />
                        </div>
                      )}

                      {progress.error && (
                        <p className="text-sm text-red-600">{progress.error}</p>
                      )}
                    </div>
                  ))}
                </div>

                {isAllCompleted && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <CheckCircle size={20} className="text-green-500" />
                      <h3 className="text-sm font-semibold text-green-900">
                        All Documents Processed
                      </h3>
                    </div>
                    <p className="text-sm text-green-800 mt-1">
                      Your documents have been successfully analyzed.
                      You can now view the risk analysis results.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Recent Uploads */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Recent Uploads
              </h2>

              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-gray-400" />
                    <span>LC_2024_001.pdf</span>
                  </div>
                  <span className="status-badge status-verified">Verified</span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-gray-400" />
                    <span>Invoice_INV_001.pdf</span>
                  </div>
                  <span className="status-badge status-warning">Warning</span>
                </div>

                <div className="flex items-center justify-between py-2">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-gray-400" />
                    <span>Certificate_001.pdf</span>
                  </div>
                  <span className="status-badge status-high">Error</span>
                </div>
              </div>

              <button className="w-full mt-4 text-sm font-medium text-green-600 hover:text-green-700 py-2">
                View All Documents
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;