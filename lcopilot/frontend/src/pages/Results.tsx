import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Hash } from 'lucide-react';
import ResultPanels from '../components/ResultPanels';
import EvidenceButton from '../components/EvidenceButton';
import QuotaBadge from '../components/QuotaBadge';
import { useResults } from '../api/hooks';
import styles from './Results.module.css';

const Results: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { data: results, isLoading, error } = useResults(jobId);

  if (!jobId) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <AlertCircle size={32} />
          <h2>Invalid Job ID</h2>
          <p>Please provide a valid job ID</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <AlertCircle size={32} />
          <h2>Failed to Load Results</h2>
          <p>The results for this job could not be loaded.</p>
          <button
            className={styles.backButton}
            onClick={() => navigate('/validate')}
          >
            <ArrowLeft size={16} />
            Back to Validation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button
          className={styles.backButton}
          onClick={() => navigate('/validate')}
        >
          <ArrowLeft size={16} />
          New Validation
        </button>

        {results.quota !== undefined && (
          <QuotaBadge quota={results.quota} usage={0} />
        )}
      </div>

      <div className={styles.resultHeader}>
        <h1>Validation Results</h1>
        <div className={styles.metadata}>
          <div className={styles.metaItem}>
            <Hash size={14} />
            <span>Job ID: {jobId}</span>
          </div>
          {results.correlationId && (
            <div className={styles.metaItem}>
              <Hash size={14} />
              <span>Correlation ID: {results.correlationId}</span>
            </div>
          )}
          {results.requestId && (
            <div className={styles.metaItem}>
              <Hash size={14} />
              <span>Request ID: {results.requestId}</span>
            </div>
          )}
        </div>
      </div>

      <div className={styles.bankInfo}>
        <div className={styles.bankName}>{results.bankProfile.name}</div>
        <div className={styles.processingTime}>
          Processed in {results.processingTime}ms
        </div>
      </div>

      <ResultPanels
        findings={results.findings}
        score={results.score}
        bankMode={false}
      />

      <div className={styles.actions}>
        <EvidenceButton
          evidenceUrl={results.evidenceUrl}
          sha256={results.evidenceSha256}
        />
      </div>

      {results.quota === 0 && (
        <div className={styles.upsell}>
          <h3>Out of Credits</h3>
          <p>You've used all your validation credits. Upgrade to continue validating documents.</p>
          <button
            className={styles.upgradeButton}
            onClick={() => navigate('/pricing')}
          >
            View Pricing Plans
          </button>
        </div>
      )}
    </div>
  );
};

export default Results;