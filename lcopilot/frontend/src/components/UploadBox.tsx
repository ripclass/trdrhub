import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, AlertCircle } from 'lucide-react';
import styles from './UploadBox.module.css';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  maxSize?: number; // in bytes
  acceptedTypes?: string[];
  disabled?: boolean;
}

const UploadBox: React.FC<UploadBoxProps> = ({
  onFileSelect,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.json'],
  disabled = false,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);

  const validateFile = (file: File): string => {
    // Check file size
    if (file.size > maxSize) {
      return `File size exceeds ${maxSize / (1024 * 1024)}MB limit`;
    }

    // Check file type
    const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
    const mimeTypes = {
      '.pdf': 'application/pdf',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.json': 'application/json',
    };

    if (!acceptedTypes.includes(extension)) {
      return `File type not supported. Accepted: ${acceptedTypes.join(', ')}`;
    }

    // Additional MIME type validation
    const expectedMime = mimeTypes[extension as keyof typeof mimeTypes];
    if (expectedMime && !file.type.includes(expectedMime.split('/')[1])) {
      return 'File content does not match extension';
    }

    return '';
  };

  const handleFile = useCallback(
    (selectedFile: File) => {
      const validationError = validateFile(selectedFile);
      if (validationError) {
        setError(validationError);
        setFile(null);
        return;
      }

      setError('');
      setFile(selectedFile);
      onFileSelect(selectedFile);
    },
    [maxSize, acceptedTypes, onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        handleFile(droppedFile);
      }
    },
    [disabled, handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) {
        handleFile(selectedFile);
      }
    },
    [handleFile]
  );

  const removeFile = useCallback(() => {
    setFile(null);
    setError('');
  }, []);

  return (
    <div className={styles.container}>
      <div
        className={`${styles.uploadBox} ${isDragging ? styles.dragging : ''} ${
          disabled ? styles.disabled : ''
        } ${error ? styles.error : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {file ? (
          <div className={styles.fileInfo}>
            <FileText size={32} />
            <div className={styles.fileName}>{file.name}</div>
            <div className={styles.fileSize}>
              {(file.size / 1024).toFixed(1)} KB
            </div>
            {!disabled && (
              <button
                className={styles.removeButton}
                onClick={removeFile}
                aria-label="Remove file"
              >
                <X size={20} />
              </button>
            )}
          </div>
        ) : (
          <div className={styles.uploadPrompt}>
            <Upload size={48} />
            <p className={styles.mainText}>
              Drop your document here or{' '}
              <label className={styles.browseButton}>
                browse
                <input
                  type="file"
                  onChange={handleFileInput}
                  accept={acceptedTypes.join(',')}
                  disabled={disabled}
                  className={styles.hiddenInput}
                />
              </label>
            </p>
            <p className={styles.helpText}>
              Supported: {acceptedTypes.join(', ')} (Max {maxSize / (1024 * 1024)}MB)
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className={styles.errorMessage} role="alert">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default UploadBox;