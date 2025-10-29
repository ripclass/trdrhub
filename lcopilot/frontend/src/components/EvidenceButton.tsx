import React, { useState } from 'react';
import { Download, Shield, CheckCircle } from 'lucide-react';
import styles from './EvidenceButton.module.css';

interface EvidenceButtonProps {
  evidenceUrl?: string;
  sha256?: string;
}

const EvidenceButton: React.FC<EvidenceButtonProps> = ({ evidenceUrl, sha256 }) => {
  const [downloading, setDownloading] = useState(false);
  const [showHash, setShowHash] = useState(false);

  const handleDownload = async () => {
    if (!evidenceUrl) return;

    setDownloading(true);
    try {
      const response = await fetch(evidenceUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evidence-pack-${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setDownloading(false);
    }
  };

  if (!evidenceUrl) {
    return null;
  }

  return (
    <div className={styles.container}>
      <button
        className={styles.downloadButton}
        onClick={handleDownload}
        disabled={downloading}
      >
        {downloading ? (
          <>
            <div className={styles.spinner} />
            <span>Downloading...</span>
          </>
        ) : (
          <>
            <Download size={20} />
            <span>Download Evidence Pack</span>
          </>
        )}
      </button>

      {sha256 && (
        <button
          className={styles.hashButton}
          onClick={() => setShowHash(!showHash)}
          aria-label="Show SHA256 hash"
        >
          <Shield size={16} />
        </button>
      )}

      {showHash && sha256 && (
        <div className={styles.hashDisplay}>
          <div className={styles.hashHeader}>
            <CheckCircle size={16} className={styles.hashIcon} />
            <span>Document Integrity</span>
          </div>
          <div className={styles.hashValue}>
            <span className={styles.hashLabel}>SHA256:</span>
            <code>{sha256}</code>
          </div>
          <p className={styles.hashInfo}>
            This hash verifies the document hasn't been tampered with.
          </p>
        </div>
      )}
    </div>
  );
};

export default EvidenceButton;