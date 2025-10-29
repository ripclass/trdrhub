import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, AlertCircle, Check } from 'lucide-react';

interface FileUploaderProps {
  onFilesSelect: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

interface FileWithPreview extends File {
  id: string;
  preview?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onFilesSelect,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.json'],
  disabled = false,
}) => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize) {
      return `${file.name}: File size exceeds ${Math.round(maxSize / (1024 * 1024))}MB limit`;
    }

    const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
    if (!acceptedTypes.includes(extension)) {
      return `${file.name}: File type not supported. Accepted: ${acceptedTypes.join(', ')}`;
    }

    return null;
  };

  const handleFiles = useCallback(
    (newFiles: FileList) => {
      const currentFileCount = files.length;
      const newFileArray = Array.from(newFiles).slice(0, maxFiles - currentFileCount);
      const validFiles: FileWithPreview[] = [];
      const newErrors: string[] = [];

      newFileArray.forEach((file) => {
        const error = validateFile(file);
        if (error) {
          newErrors.push(error);
        } else {
          const fileWithId = Object.assign(file, {
            id: `${file.name}-${Date.now()}-${Math.random()}`,
          }) as FileWithPreview;
          validFiles.push(fileWithId);
        }
      });

      if (validFiles.length > 0) {
        const updatedFiles = [...files, ...validFiles];
        setFiles(updatedFiles);
        onFilesSelect(updatedFiles);
      }

      setErrors(newErrors);
    },
    [files, maxFiles, maxSize, acceptedTypes, onFilesSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      handleFiles(e.dataTransfer.files);
    },
    [disabled, handleFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        handleFiles(e.target.files);
      }
    },
    [handleFiles]
  );

  const removeFile = useCallback(
    (fileId: string) => {
      const updatedFiles = files.filter((f) => f.id !== fileId);
      setFiles(updatedFiles);
      onFilesSelect(updatedFiles);
    },
    [files, onFilesSelect]
  );

  const getFileTypeIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FileText className="text-red-500" size={20} />;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <FileText className="text-blue-500" size={20} />;
      case 'json':
        return <FileText className="text-green-500" size={20} />;
      default:
        return <FileText className="text-gray-500" size={20} />;
    }
  };

  const getFileTypeLabel = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return 'LC Document';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return 'Supporting Image';
      case 'json':
        return 'Data File';
      default:
        return 'Document';
    }
  };

  return (
    <div className="w-full">
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging ? 'border-green-500 bg-green-50' : 'border-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-400'}
          ${files.length >= maxFiles ? 'opacity-50' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          accept={acceptedTypes.join(',')}
          disabled={disabled || files.length >= maxFiles}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="space-y-4">
          <Upload
            size={48}
            className={`mx-auto ${isDragging ? 'text-green-500' : 'text-gray-400'}`}
          />

          <div>
            <p className="text-lg font-medium text-gray-900">
              {files.length === 0 ? 'Drop your documents here' : 'Add more documents'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or <span className="text-green-600 font-medium">browse files</span>
            </p>
          </div>

          <p className="text-xs text-gray-400">
            Supports: {acceptedTypes.join(', ')} • Max {Math.round(maxSize / (1024 * 1024))}MB each • Up to {maxFiles} files
          </p>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="mt-4 space-y-2">
          {errors.map((error, index) => (
            <div key={index} className="flex items-center gap-2 text-red-600 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          ))}
        </div>
      )}

      {/* File Preview List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="text-sm font-medium text-gray-900">
            Selected Files ({files.length}/{maxFiles})
          </h4>

          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  {getFileTypeIcon(file.name)}

                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{(file.size / 1024).toFixed(1)} KB</span>
                      <span className="status-badge status-low">
                        {getFileTypeLabel(file.name)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Check size={16} className="text-green-500" />
                  {!disabled && (
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      aria-label={`Remove ${file.name}`}
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;