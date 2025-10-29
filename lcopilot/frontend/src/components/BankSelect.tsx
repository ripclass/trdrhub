import React from 'react'
import styles from './BankSelect.module.css'

interface Bank {
  code: string
  name: string
  description?: string
}

interface BankSelectProps {
  banks: Bank[]
  selectedBank: string
  onBankChange?: (bankCode: string) => void
  onSelect?: (bankCode: string) => void
  disabled?: boolean
}

export default function BankSelect({ 
  banks, 
  selectedBank, 
  onBankChange, 
  onSelect,
  disabled = false 
}: BankSelectProps) {
  return (
    <div className={styles.bankSelect}>
      <label htmlFor="bank-select" className={styles.label}>
        Select Bank Profile
      </label>
      <select
        id="bank-select"
        value={selectedBank}
        onChange={(e) => (onBankChange || onSelect)?.(e.target.value)}
        disabled={disabled}
        className={styles.select}
      >
        <option value="">Choose a bank...</option>
        {banks.map((bank) => (
          <option key={bank.code} value={bank.code}>
            {bank.name}
          </option>
        ))}
      </select>
    </div>
  )
}
