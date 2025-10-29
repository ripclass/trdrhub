import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { usePaymentCallback } from '../api/hooks';
import styles from './BillingCallback.module.css';

const BillingCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const paymentCallback = usePaymentCallback();

  useEffect(() => {
    // Process the payment callback
    if (searchParams.toString()) {
      paymentCallback.mutate(searchParams);
    }
  }, [searchParams]);

  const renderContent = () => {
    if (paymentCallback.isPending) {
      return (
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <h2>Processing Payment</h2>
          <p>Please wait while we confirm your payment...</p>
        </div>
      );
    }

    if (paymentCallback.isError) {
      return (
        <div className={styles.error}>
          <XCircle size={48} />
          <h2>Payment Failed</h2>
          <p>There was an issue processing your payment. Please try again.</p>
          <button
            className={styles.button}
            onClick={() => navigate('/pricing')}
          >
            Back to Pricing
          </button>
        </div>
      );
    }

    if (paymentCallback.data) {
      const { status, transactionId, amount, quota, message } = paymentCallback.data;

      if (status === 'success') {
        return (
          <div className={styles.success}>
            <CheckCircle size={48} />
            <h2>Payment Successful!</h2>
            <p>Your payment has been processed successfully.</p>

            <div className={styles.details}>
              {transactionId && (
                <div className={styles.detailItem}>
                  <span className={styles.label}>Transaction ID:</span>
                  <span className={styles.value}>{transactionId}</span>
                </div>
              )}
              {amount && (
                <div className={styles.detailItem}>
                  <span className={styles.label}>Amount:</span>
                  <span className={styles.value}>৳{amount.toLocaleString('en-BD')}</span>
                </div>
              )}
              {quota !== undefined && (
                <div className={styles.detailItem}>
                  <span className={styles.label}>Credits Added:</span>
                  <span className={styles.value}>{quota}</span>
                </div>
              )}
            </div>

            <button
              className={styles.primaryButton}
              onClick={() => navigate('/validate')}
            >
              Start Validating
            </button>
          </div>
        );
      }

      if (status === 'cancelled') {
        return (
          <div className={styles.cancelled}>
            <AlertCircle size={48} />
            <h2>Payment Cancelled</h2>
            <p>{message || 'You cancelled the payment process.'}</p>
            <button
              className={styles.button}
              onClick={() => navigate('/pricing')}
            >
              Back to Pricing
            </button>
          </div>
        );
      }

      return (
        <div className={styles.error}>
          <XCircle size={48} />
          <h2>Payment Failed</h2>
          <p>{message || 'The payment could not be processed.'}</p>
          <button
            className={styles.button}
            onClick={() => navigate('/pricing')}
          >
            Try Again
          </button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {renderContent()}
      </div>
    </div>
  );
};

export default BillingCallback;