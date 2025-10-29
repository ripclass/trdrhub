import React from 'react'
import styles from './ProgressStrip.module.css'

interface ProgressStripProps {
  progress: number
  stage: string
  className?: string
}

export default function ProgressStrip({ 
  progress, 
  stage, 
  className = '' 
}: ProgressStripProps) {
  return (
    <div className={`${styles.progressStrip} ${className}`}>
      <div className={styles.progressInfo}>
        <span className={styles.stage}>{stage}</span>
        <span className={styles.percentage}>{progress}%</span>
      </div>
      <div className={styles.progressBar}>
        <div 
          className={styles.progressFill}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
