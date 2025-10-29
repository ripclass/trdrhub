import React from 'react';
import { Zap, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import styles from './QuotaBadge.module.css';

interface QuotaBadgeProps {
  quota?: number;
  usage?: number;
  showUpgrade?: boolean;
}

const QuotaBadge: React.FC<QuotaBadgeProps> = ({
  quota = 0,
  usage = 0,
  showUpgrade = true
}) => {
  const navigate = useNavigate();
  const remaining = Math.max(0, quota - usage);
  const percentageUsed = quota > 0 ? (usage / quota) * 100 : 100;

  const getStatusClass = () => {
    if (remaining === 0) return styles.critical;
    if (percentageUsed > 80) return styles.warning;
    return styles.normal;
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  return (
    <div className={`${styles.container} ${getStatusClass()}`}>
      <div className={styles.badge}>
        <Zap size={16} />
        <span className={styles.count}>{remaining}</span>
        <span className={styles.label}>checks left</span>
      </div>

      {showUpgrade && remaining <= 5 && (
        <button
          className={styles.upgradeButton}
          onClick={handleUpgrade}
          aria-label="Top up credits"
        >
          Top up
          <ArrowRight size={14} />
        </button>
      )}

      {remaining === 0 && (
        <div className={styles.alert}>
          <p>You've used all your validation credits.</p>
          {showUpgrade && (
            <button
              className={styles.upgradeCTA}
              onClick={handleUpgrade}
            >
              Get more credits
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default QuotaBadge;