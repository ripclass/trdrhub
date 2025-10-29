import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertCircle, FileText } from 'lucide-react';
import ProgressStrip from '../components/ProgressStrip';
import { useJob } from '../api/hooks';
import { useError } from '../contexts/ErrorContext';
import styles from './Job.module.css';

const Job: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { showError } = useError();
  const { data: job, error } = useJob(jobId);

  useEffect(() => {
    if (job?.status === 'completed') {
      // Redirect to results page when job completes
      navigate(`/results/${jobId}`, { replace: true });
    }
  }, [job?.status, jobId, navigate]);

  useEffect(() => {
    if (error) {
      showError({
        error_id: 'job_fetch_error',
        type: 'api',
        message: 'Failed to fetch job status',
      });
    }
  }, [error, showError]);

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

  if (!job) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading job status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.icon}>
          <FileText size={32} />
        </div>
        <h1>Processing Your Document</h1>
        <p className={styles.jobId}>Job ID: {jobId}</p>
        {job.requestId && (
          <p className={styles.requestId}>Request ID: {job.requestId}</p>
        )}
      </div>

      <div className={styles.content}>
        <ProgressStrip
          currentStage={job.stage}
          error={job.status === 'failed'}
        />

        {job.status === 'failed' && job.error && (
          <div className={styles.errorDetails}>
            <h3>Processing Failed</h3>
            <p>{job.error.message}</p>
            {job.error.error_id && (
              <p className={styles.errorId}>Error ID: {job.error.error_id}</p>
            )}
            <button
              className={styles.retryButton}
              onClick={() => navigate('/validate')}
            >
              Try Again
            </button>
          </div>
        )}

        <div className={styles.info}>
          <div className={styles.infoItem}>
            <span className={styles.label}>Status:</span>
            <span className={`${styles.status} ${styles[job.status]}`}>
              {job.status}
            </span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.label}>Stage:</span>
            <span>{job.stage}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.label}>Progress:</span>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${job.progress}%` }}
              />
            </div>
            <span className={styles.progressText}>{job.progress}%</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.label}>Started:</span>
            <span>{new Date(job.createdAt).toLocaleString()}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.label}>Last Update:</span>
            <span>{new Date(job.updatedAt).toLocaleString()}</span>
          </div>
        </div>

        <div className={styles.helpText}>
          <p>
            Your document is being processed. This typically takes 30-60 seconds
            depending on document size and complexity.
          </p>
          <p>
            You can safely leave this page and return later. We'll save your results.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Job;