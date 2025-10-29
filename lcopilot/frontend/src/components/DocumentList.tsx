import React from 'react';
import { FileText, Eye, Download, AlertTriangle, CheckCircle, Clock, MoreVertical } from 'lucide-react';

export type DocumentStatus = 'pending' | 'processing' | 'verified' | 'warning' | 'error';
export type DocumentType = 'LC' | 'invoice' | 'certificate' | 'contract' | 'other';

interface Document {
  id: string;
  name: string;
  type: DocumentType;
  status: DocumentStatus;
  uploadDate: Date;
  lastModified: Date;
  size: number;
  riskScore?: number;
  issues?: string[];
  downloadUrl?: string;
  previewUrl?: string;
}

interface DocumentListProps {
  documents: Document[];
  onView?: (document: Document) => void;
  onDownload?: (document: Document) => void;
  onDelete?: (documentId: string) => void;
  showActions?: boolean;
  compact?: boolean;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onView,
  onDownload,
  onDelete,
  showActions = true,
  compact = false,
}) => {
  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case 'verified':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'warning':
        return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'error':
        return <AlertTriangle size={16} className="text-red-500" />;
      case 'processing':
        return <Clock size={16} className="text-blue-500 animate-pulse" />;
      default:
        return <Clock size={16} className="text-gray-400" />;
    }
  };

  const getStatusBadge = (status: DocumentStatus) => {
    switch (status) {
      case 'verified':
        return 'status-badge status-verified';
      case 'warning':
        return 'status-badge status-warning';
      case 'error':
        return 'status-badge status-high';
      case 'processing':
        return 'status-badge bg-blue-100 text-blue-800';
      default:
        return 'status-badge bg-gray-100 text-gray-600';
    }
  };

  const getDocumentTypeIcon = (_type: DocumentType) => {
    return <FileText size={20} className="text-gray-600" />;
  };

  const getDocumentTypeLabel = (type: DocumentType) => {
    switch (type) {
      case 'LC':
        return 'Letter of Credit';
      case 'invoice':
        return 'Invoice';
      case 'certificate':
        return 'Certificate';
      case 'contract':
        return 'Contract';
      default:
        return 'Document';
    }
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-blue-600';
    return 'text-green-600';
  };

  if (documents.length === 0) {
    return (
      <div className="card p-8 text-center">
        <FileText size={48} className="mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500">No documents uploaded</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((document) => (
        <div key={document.id} className="card p-4 hover:shadow-md transition-shadow">
          <div className="flex items-start gap-3">
            {/* Document Icon */}
            <div className="flex-shrink-0 mt-1">
              {getDocumentTypeIcon(document.type)}
            </div>

            {/* Document Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {document.name}
                  </h4>
                  <p className="text-xs text-gray-500">
                    {getDocumentTypeLabel(document.type)}
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  {getStatusIcon(document.status)}
                  <span className={getStatusBadge(document.status)}>
                    {document.status}
                  </span>
                </div>
              </div>

              {/* Document Details */}
              {!compact && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500 mb-3">
                  <div>
                    <span className="font-medium">Size:</span> {formatFileSize(document.size)}
                  </div>
                  <div>
                    <span className="font-medium">Uploaded:</span> {formatDate(document.uploadDate)}
                  </div>
                  <div>
                    <span className="font-medium">Modified:</span> {formatDate(document.lastModified)}
                  </div>
                  {document.riskScore !== undefined && (
                    <div>
                      <span className="font-medium">Risk Score:</span>{' '}
                      <span className={`font-semibold ${getRiskScoreColor(document.riskScore)}`}>
                        {document.riskScore}%
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Issues */}
              {document.issues && document.issues.length > 0 && (
                <div className="mb-3">
                  <h5 className="text-xs font-medium text-gray-700 mb-1">Issues Found:</h5>
                  <div className="space-y-1">
                    {document.issues.slice(0, compact ? 1 : 3).map((issue, index) => (
                      <div key={index} className="flex items-start gap-2 text-xs text-red-600">
                        <AlertTriangle size={12} className="flex-shrink-0 mt-0.5" />
                        <span>{issue}</span>
                      </div>
                    ))}
                    {document.issues.length > (compact ? 1 : 3) && (
                      <p className="text-xs text-gray-500 ml-4">
                        +{document.issues.length - (compact ? 1 : 3)} more issues
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              {showActions && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {onView && (
                      <button
                        onClick={() => onView(document)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 hover:bg-green-100 rounded-md transition-colors"
                      >
                        <Eye size={14} />
                        View
                      </button>
                    )}

                    {onDownload && document.downloadUrl && (
                      <button
                        onClick={() => onDownload(document)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        <Download size={14} />
                        Download
                      </button>
                    )}
                  </div>

                  {onDelete && (
                    <button
                      onClick={() => onDelete(document.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      aria-label={`Delete ${document.name}`}
                    >
                      <MoreVertical size={16} />
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;