import React from 'react';
import { Check, Zap } from 'lucide-react';
import { useSSLCommerzCheckout } from '../api/hooks';
import styles from './Pricing.module.css';

const Pricing: React.FC = () => {
  const checkout = useSSLCommerzCheckout();

  const tiers = [
    {
      range: '1-20 checks',
      pricePerCheck: 1200,
      totalPrice: 24000,
      checks: 20,
      features: [
        'LC Document Validation',
        'All Bank Profiles',
        'Evidence Pack Generation',
        'Email Support',
      ],
      popular: false,
    },
    {
      range: '21-50 checks',
      pricePerCheck: 999,
      totalPrice: 29970,
      checks: 30,
      features: [
        'Everything in Starter',
        'Priority Processing',
        'API Access',
        'Phone Support',
      ],
      popular: true,
    },
    {
      range: '50+ checks',
      pricePerCheck: 699,
      totalPrice: 34950,
      checks: 50,
      features: [
        'Everything in Professional',
        'Bulk Upload',
        'Custom Bank Profiles',
        'Dedicated Account Manager',
      ],
      popular: false,
    },
  ];

  const handlePurchase = (checks: number, amount: number) => {
    checkout.mutate({ checks, amount });
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Simple, Transparent Pricing</h1>
        <p>Pay per validation check. No monthly fees. No hidden costs.</p>
      </div>

      <div className={styles.tiers}>
        {tiers.map((tier, index) => (
          <div
            key={index}
            className={`${styles.tier} ${tier.popular ? styles.popular : ''}`}
          >
            {tier.popular && (
              <div className={styles.popularBadge}>Most Popular</div>
            )}

            <div className={styles.tierHeader}>
              <h3>{tier.range}</h3>
              <div className={styles.price}>
                <span className={styles.currency}>৳</span>
                <span className={styles.amount}>{tier.pricePerCheck}</span>
                <span className={styles.unit}>per check</span>
              </div>
              <div className={styles.totalPrice}>
                Total: ৳{tier.totalPrice.toLocaleString('en-BD')}
              </div>
            </div>

            <ul className={styles.features}>
              {tier.features.map((feature, idx) => (
                <li key={idx}>
                  <Check size={16} />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            <button
              className={`${styles.purchaseButton} ${
                tier.popular ? styles.purchaseButtonPrimary : ''
              }`}
              onClick={() => handlePurchase(tier.checks, tier.totalPrice)}
              disabled={checkout.isPending}
            >
              {checkout.isPending ? (
                <>
                  <div className={styles.spinner} />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Zap size={16} />
                  <span>Get {tier.checks} Checks</span>
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      <div className={styles.faq}>
        <h2>Frequently Asked Questions</h2>

        <div className={styles.faqItem}>
          <h3>How does pricing work?</h3>
          <p>
            You purchase validation credits upfront. Each credit allows you to
            validate one LC document. Credits never expire.
          </p>
        </div>

        <div className={styles.faqItem}>
          <h3>What payment methods do you accept?</h3>
          <p>
            We accept all major cards, mobile banking (bKash, Nagad), and bank
            transfers through SSLCommerz.
          </p>
        </div>

        <div className={styles.faqItem}>
          <h3>Can I get a refund?</h3>
          <p>
            Unused credits can be refunded within 30 days of purchase. Please
            contact support for assistance.
          </p>
        </div>

        <div className={styles.faqItem}>
          <h3>Do you offer enterprise pricing?</h3>
          <p>
            Yes! For volumes over 100 checks per month, contact us for custom
            pricing and dedicated support.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Pricing;