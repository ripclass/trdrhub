import React from 'react'
import styles from './ResultPanels.module.css'

interface ResultPanelsProps {
  results: any
  className?: string
}

export default function ResultPanels({ 
  results, 
  className = '' 
}: ResultPanelsProps) {
  return (
    <div className={`${styles.resultPanels} ${className}`}>
      <div className={styles.panel}>
        <h3>Validation Results</h3>
        <p>Results will be displayed here</p>
      </div>
    </div>
  )
}
