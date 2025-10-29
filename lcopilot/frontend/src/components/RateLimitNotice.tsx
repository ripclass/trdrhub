import React from 'react';
import { AlertTriangle, Clock, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import styles from './RateLimitNotice.module.css';

interface RateLimitNoticeProps {
  message?: string;
  retryAfter?: number;
}

const RateLimitNotice: React.FC<RateLimitNoticeProps> = ({
  message = 'You have exceeded your rate limit. Please upgrade your plan or try again later.',
  retryAfter
}) => {
  const navigate = useNavigate();

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  return (
    <div className={styles.container}>
      <div className={styles.icon}>
        <AlertTriangle size={32} />
      </div>

      <h3 className={styles.title}>Rate Limit Exceeded</h3>

      <p className={styles.message}>{message}</p>

      {retryAfter && (
        <div className={styles.retryInfo}>
          <Clock size={16} />
          <span>Try again in {Math.ceil(retryAfter / 60)} minutes</span>
        </div>
      )}

      <div className={styles.actions}>
        <button
          className={styles.primaryButton}
          onClick={handleUpgrade}
        >
          <Zap size={16} />
          Upgrade Plan
        </button>

        <button
          className={styles.secondaryButton}
          onClick={() => window.history.back()}
        >
          Go Back
        </button>
      </div>

      <div className={styles.helpText}>
        <p>Need more validations? Our Pro and Enterprise plans offer:</p>
        <ul>
          <li>Higher rate limits</li>
          <li>Priority processing</li>
          <li>Bulk validation support</li>
          <li>Advanced API access</li>
        </ul>
      </div>
    </div>
  );
};

export default RateLimitNotice;