import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Settings } from 'lucide-react';
import UploadBox from '../components/UploadBox';
import BankSelect from '../components/BankSelect';
import RateLimitNotice from '../components/RateLimitNotice';
import QuotaBadge from '../components/QuotaBadge';
import { useCreateValidation, useBankProfiles, useCurrentUser } from '../api/hooks';
import { useError } from '../contexts/ErrorContext';
import styles from './Validate.module.css';

const Validate: React.FC = () => {
  const navigate = useNavigate();
  const { showError } = useError();
  const [file, setFile] = useState<File | null>(null);
  const [selectedBank, setSelectedBank] = useState('');
  const [asyncMode, setAsyncMode] = useState(true);
  const [showRateLimit, setShowRateLimit] = useState(false);

  const { data: banks = [], isLoading: banksLoading } = useBankProfiles();
  const { data: user } = useCurrentUser();
  const createValidation = useCreateValidation();

  const handleFileSelect = useCallback((file: File) => {
    setFile(file);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !selectedBank) {
      showError({
        error_id: 'validation_error',
        type: 'validation',
        message: 'Please select a file and bank profile',
      });
      return;
    }

    try {
      const result = await createValidation.mutateAsync({
        file,
        bankCode: selectedBank,
        async: asyncMode,
      });

      if (asyncMode) {
        navigate(`/jobs/${result.jobId}`);
      } else {
        navigate(`/results/${result.jobId}`);
      }
    } catch (error: any) {
      if (error.type === 'rate_limit') {
        setShowRateLimit(true);
      } else {
        showError(error);
      }
    }
  };

  if (showRateLimit) {
    return <RateLimitNotice />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>LC Validation</h1>
        {user && (
          <QuotaBadge
            quota={user.quota}
            usage={user.usage}
          />
        )}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.section}>
          <h2>1. Upload Document</h2>
          <UploadBox
            onFileSelect={handleFileSelect}
            disabled={createValidation.isPending}
          />
        </div>

        <div className={styles.section}>
          <h2>2. Select Bank Profile</h2>
          {banksLoading ? (
            <div className={styles.loading}>Loading banks...</div>
          ) : (
            <BankSelect
              banks={banks}
              selectedBank={selectedBank}
              onSelect={setSelectedBank}
              disabled={createValidation.isPending}
            />
          )}
        </div>

        <div className={styles.section}>
          <h2>3. Processing Mode</h2>
          <div className={styles.modeToggle}>
            <label className={styles.toggleLabel}>
              <input
                type="checkbox"
                checked={asyncMode}
                onChange={(e) => setAsyncMode(e.target.checked)}
                disabled={createValidation.isPending}
              />
              <span className={styles.toggleSlider} />
              <span className={styles.toggleText}>
                {asyncMode ? 'Asynchronous (Recommended)' : 'Synchronous'}
              </span>
            </label>
            <div className={styles.modeInfo}>
              <Settings size={16} />
              <span>
                {asyncMode
                  ? 'Process in background and track progress'
                  : 'Wait for immediate results (may timeout for large files)'}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.actions}>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={!file || !selectedBank || createValidation.isPending}
          >
            {createValidation.isPending ? (
              <>
                <div className={styles.spinner} />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle size={20} />
                <span>Validate Document</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Validate;