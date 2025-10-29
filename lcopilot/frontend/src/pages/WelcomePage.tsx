import React from 'react'
import { Link } from 'react-router-dom'
import { FileText, CheckCircle, AlertTriangle, Download } from 'lucide-react'

export default function WelcomePage() {
  return (
    <div className="container">
      <div className="card">
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1f2937' }}>
          LCopilot
        </h1>
        <p style={{ fontSize: '1.125rem', color: '#6b7280', marginBottom: '2rem' }}>
          Letter of Credit Validation Platform
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          <div style={{ textAlign: 'center', padding: '1.5rem' }}>
            <FileText size={48} style={{ color: '#3b82f6', margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Upload LC</h3>
            <p style={{ color: '#6b7280' }}>Upload your Letter of Credit document for validation</p>
          </div>
          
          <div style={{ textAlign: 'center', padding: '1.5rem' }}>
            <CheckCircle size={48} style={{ color: '#10b981', margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>OCR & Validation</h3>
            <p style={{ color: '#6b7280' }}>Automated OCR extraction and Fatal Four validation</p>
          </div>
          
          <div style={{ textAlign: 'center', padding: '1.5rem' }}>
            <AlertTriangle size={48} style={{ color: '#f59e0b', margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Review Discrepancies</h3>
            <p style={{ color: '#6b7280' }}>Review identified discrepancies and validation results</p>
          </div>
          
          <div style={{ textAlign: 'center', padding: '1.5rem' }}>
            <Download size={48} style={{ color: '#8b5cf6', margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Download Report</h3>
            <p style={{ color: '#6b7280' }}>Generate and download PDF validation report</p>
          </div>
        </div>
        
        <Link to="/upload" className="btn btn-primary" style={{ fontSize: '1.125rem', padding: '1rem 2rem' }}>
          Start Validation Process
        </Link>
      </div>
    </div>
  )
}