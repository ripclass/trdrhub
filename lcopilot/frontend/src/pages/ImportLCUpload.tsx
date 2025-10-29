import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Shield, FileText, Upload as UploadIcon, CheckCircle } from 'lucide-react';
import FileUploader from '../components/FileUploader';
import { useValidate } from '../hooks/useApi';
import { useToast } from '../components/Toast';

const ImportLCUpload: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedWorkflow, setSelectedWorkflow] = useState<'draft-lc-risk' | 'supplier-document-check' | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [checkedDocuments, setCheckedDocuments] = useState<string[]>([]);

  const validateMutation = useValidate();
  const { showToast } = useToast();

  // Initialize workflow from URL params
  useEffect(() => {
    const workflow = searchParams.get('workflow') as 'draft-lc-risk' | 'supplier-document-check';
    if (workflow) {
      setSelectedWorkflow(workflow);
    }
  }, [searchParams]);

  const workflowConfigs = {
    'draft-lc-risk': {
      title: 'Draft LC Risk Analysis',
      description: 'Upload your draft LC for comprehensive risk assessment and clause analysis',
      icon: Shield,
      color: 'blue',
      price: '৳200',
      documents: [
        {
          id: 'draft-lc',
          name: 'Draft Letter of Credit',
          description: 'Draft LC document from your bank',
          required: true,
          extensions: ['.pdf']
        },
        {
          id: 'purchase-order',
          name: 'Purchase Order',
          description: 'Original purchase order or contract',
          required: false,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        },
        {
          id: 'proforma-invoice',
          name: 'Proforma Invoice',
          description: 'Supplier\'s proforma invoice',
          required: false,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        }
      ]
    },
    'supplier-document-check': {
      title: 'Supplier Document Check',
      description: 'Upload supplier documents for compliance verification against LC terms',
      icon: FileText,
      color: 'green',
      price: '৳180',
      documents: [
        {
          id: 'lc',
          name: 'Letter of Credit',
          description: 'Current LC for reference',
          required: true,
          extensions: ['.pdf']
        },
        {
          id: 'supplier-invoice',
          name: 'Supplier Invoice',
          description: 'Commercial invoice from supplier',
          required: true,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        },
        {
          id: 'packing-list',
          name: 'Packing List',
          description: 'Detailed packing information',
          required: true,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        },
        {
          id: 'bl',
          name: 'Bill of Lading',
          description: 'Transport document',
          required: true,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        },
        {
          id: 'certificate',
          name: 'Certificates',
          description: 'Origin, quality, or inspection certificates',
          required: false,
          extensions: ['.pdf', '.jpg', '.jpeg', '.png']
        }
      ]
    }
  };

  const handleWorkflowSelect = (workflow: 'draft-lc-risk' | 'supplier-document-check') => {
    setSelectedWorkflow(workflow);
    setSelectedFiles([]);
    setCheckedDocuments([]);
  };

  const handleDocumentCheck = (docId: string) => {
    setCheckedDocuments(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleFilesSelect = (files: File[]) => {
    setSelectedFiles(files);
  };

  const handleSubmit = async () => {
    if (!selectedWorkflow) {
      showToast({
        type: 'warning',
        title: 'Workflow Not Selected',
        message: 'Please select a workflow before proceeding.'
      });
      return;
    }

    if (selectedFiles.length === 0) {
      showToast({
        type: 'warning',
        title: 'No Files Selected',
        message: 'Please upload at least one document to proceed.'
      });
      return;
    }

    const config = workflowConfigs[selectedWorkflow];
    const requiredDocs = config.documents.filter(doc => doc.required);
    const missingRequired = requiredDocs.filter(doc => !checkedDocuments.includes(doc.id));

    if (missingRequired.length > 0) {
      showToast({
        type: 'warning',
        title: 'Missing Required Documents',
        message: `Please confirm you have: ${missingRequired.map(doc => doc.name).join(', ')}`
      });
      return;
    }

    try {
      const result = await validateMutation.mutateAsync({
        files: selectedFiles,
        user_type: 'importer',
        workflow_type: selectedWorkflow
      });

      showToast({
        type: 'success',
        title: 'Analysis Started',
        message: `Job ${result.job_id} created successfully. Redirecting to results...`
      });

      // Redirect to appropriate results page
      setTimeout(() => {
        if (selectedWorkflow === 'draft-lc-risk') {
          navigate(`/draft-lc-risk-results/${result.job_id}`);
        } else {
          navigate(`/supplier-document-results/${result.job_id}`);
        }
      }, 1000);

    } catch (error) {
      showToast({
        type: 'error',
        title: 'Analysis Failed',
        message: error instanceof Error ? error.message : 'An error occurred while starting analysis.'
      });
    }
  };

  const currentConfig = selectedWorkflow ? workflowConfigs[selectedWorkflow] : null;
  const allRequiredChecked = currentConfig
    ? currentConfig.documents
        .filter(doc => doc.required)
        .every(doc => checkedDocuments.includes(doc.id))
    : false;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/importer-dashboard')}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Import Document Upload</h1>
          <p className="text-gray-600 mt-1">
            Choose your workflow and upload documents for analysis
          </p>
        </div>

        {/* Workflow Selection */}
        {!selectedWorkflow && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Choose Your Workflow
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <button
                onClick={() => handleWorkflowSelect('draft-lc-risk')}
                className="text-left p-6 border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Shield size={24} className="text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Draft LC Risk Analysis
                    </h3>
                    <p className="text-sm text-gray-600">৳200 per analysis</p>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Comprehensive risk assessment of draft LC clauses, terms, and conditions
                  before finalization with your bank.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>Clause risk scoring</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>UCP 600 compliance check</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>Amendment recommendations</span>
                  </li>
                </ul>
              </button>

              <button
                onClick={() => handleWorkflowSelect('supplier-document-check')}
                className="text-left p-6 border-2 border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <FileText size={24} className="text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Supplier Document Check
                    </h3>
                    <p className="text-sm text-gray-600">৳180 per analysis</p>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Verify supplier documents against LC terms to identify discrepancies
                  and ensure compliance before payment.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>Document authenticity check</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>LC compliance verification</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-green-500" />
                    <span>Discrepancy reporting</span>
                  </li>
                </ul>
              </button>
            </div>
          </div>
        )}

        {/* Selected Workflow Content */}
        {selectedWorkflow && currentConfig && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Upload Area */}
            <div className="lg:col-span-2 space-y-8">
              {/* Workflow Header */}
              <div className="card p-6 bg-gradient-to-r from-blue-50 to-green-50">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-12 h-12 bg-${currentConfig.color}-100 rounded-lg flex items-center justify-center`}>
                    <currentConfig.icon size={24} className={`text-${currentConfig.color}-600`} />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {currentConfig.title}
                    </h2>
                    <p className="text-sm text-gray-600">
                      {currentConfig.description}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedWorkflow(null)}
                  className="text-sm font-medium text-green-600 hover:text-green-700"
                >
                  ← Change Workflow
                </button>
              </div>

              {/* Document Upload */}
              <section className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Upload Documents
                </h3>

                <FileUploader
                  onFilesSelect={handleFilesSelect}
                  maxFiles={10}
                  maxSize={25 * 1024 * 1024}
                  acceptedTypes={['.pdf', '.jpg', '.jpeg', '.png']}
                  disabled={validateMutation.isPending}
                />

                {selectedFiles.length > 0 && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 text-green-800">
                      <CheckCircle size={16} />
                      <span className="text-sm font-medium">
                        {selectedFiles.length} documents ready for analysis
                      </span>
                    </div>
                  </div>
                )}
              </section>

              {/* Document Verification */}
              <section className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Document Verification Checklist
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Please confirm that you have uploaded the following documents:
                </p>

                <div className="space-y-4">
                  {currentConfig.documents.map((doc) => (
                    <label
                      key={doc.id}
                      className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={checkedDocuments.includes(doc.id)}
                        onChange={() => handleDocumentCheck(doc.id)}
                        className="mt-1 h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                      />

                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900">{doc.name}</h4>
                          {doc.required && (
                            <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded-full font-medium">
                              Required
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{doc.description}</p>
                        <p className="text-xs text-gray-500">
                          Accepted formats: {doc.extensions.join(', ')}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </section>

              {/* Submit Section */}
              <section className="card p-6 bg-gradient-to-r from-primary-50 to-blue-50">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Ready for Analysis</h3>
                    <p className="text-sm text-gray-600">
                      Analysis typically takes 1-3 minutes
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">{currentConfig.price}</div>
                    <div className="text-sm text-gray-600">per analysis</div>
                  </div>
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={!allRequiredChecked || selectedFiles.length === 0 || validateMutation.isPending}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {validateMutation.isPending ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Starting Analysis...
                    </>
                  ) : (
                    <>
                      <UploadIcon size={18} />
                      Start {currentConfig.title}
                    </>
                  )}
                </button>

                {(!allRequiredChecked || selectedFiles.length === 0) && (
                  <p className="text-xs text-gray-500 text-center mt-2">
                    {selectedFiles.length === 0
                      ? 'Please upload documents to continue'
                      : 'Please verify all required documents are included'
                    }
                  </p>
                )}
              </section>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Analysis Process */}
              <section className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Analysis Process
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      1
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Upload Documents</div>
                      <div className="text-sm text-gray-600">Select and upload required files</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      2
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">AI Analysis</div>
                      <div className="text-sm text-gray-600">
                        {selectedWorkflow === 'draft-lc-risk' ? 'Risk assessment' : 'Compliance check'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      3
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Review Results</div>
                      <div className="text-sm text-gray-600">Detailed findings and recommendations</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      4
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Take Action</div>
                      <div className="text-sm text-gray-600">
                        {selectedWorkflow === 'draft-lc-risk' ? 'Request amendments' : 'Address discrepancies'}
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* What We Analyze */}
              <section className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  What We {selectedWorkflow === 'draft-lc-risk' ? 'Analyze' : 'Check'}
                </h3>
                <div className="space-y-3 text-sm">
                  {selectedWorkflow === 'draft-lc-risk' ? (
                    <>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Clause ambiguity detection</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Payment term risks</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Document requirement clarity</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Shipment term analysis</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Timeline feasibility</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>UCP 600 compliance</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Document authenticity</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>LC term compliance</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Mathematical accuracy</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Date validations</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Format requirements</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-green-500" />
                        <span>Discrepancy identification</span>
                      </div>
                    </>
                  )}
                </div>
              </section>

              {/* Support */}
              <section className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Need Help?
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Questions about document requirements or upload process?
                </p>
                <div className="space-y-2">
                  <button className="w-full btn-secondary text-sm">
                    View Upload Guide
                  </button>
                  <button className="w-full btn-secondary text-sm">
                    Contact Support
                  </button>
                </div>
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportLCUpload;