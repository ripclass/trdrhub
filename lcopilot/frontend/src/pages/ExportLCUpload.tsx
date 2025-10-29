import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, CheckCircle, Upload as UploadIcon } from 'lucide-react';
import FileUploader from '../components/FileUploader';
import { useValidate } from '../hooks/useApi';
import { useToast } from '../components/Toast';

const ExportLCUpload: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [checkedDocuments, setCheckedDocuments] = useState<string[]>([]);

  const validateMutation = useValidate();
  const { showToast } = useToast();

  const requiredDocuments = [
    {
      id: 'lc',
      name: 'Letter of Credit (LC)',
      description: 'Original LC issued by the importing bank',
      required: true,
      extensions: ['.pdf']
    },
    {
      id: 'invoice',
      name: 'Commercial Invoice',
      description: 'Detailed invoice matching LC terms',
      required: true,
      extensions: ['.pdf', '.jpg', '.jpeg', '.png']
    },
    {
      id: 'packing',
      name: 'Packing List',
      description: 'Detailed packing and weight information',
      required: true,
      extensions: ['.pdf', '.jpg', '.jpeg', '.png']
    },
    {
      id: 'bl',
      name: 'Bill of Lading',
      description: 'Transport document for goods shipment',
      required: true,
      extensions: ['.pdf', '.jpg', '.jpeg', '.png']
    },
    {
      id: 'coo',
      name: 'Certificate of Origin',
      description: 'Government-issued origin certificate',
      required: true,
      extensions: ['.pdf', '.jpg', '.jpeg', '.png']
    },
    {
      id: 'insurance',
      name: 'Insurance Certificate',
      description: 'Marine insurance coverage certificate',
      required: false,
      extensions: ['.pdf', '.jpg', '.jpeg', '.png']
    }
  ];

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
    // Validation
    if (selectedFiles.length === 0) {
      showToast({
        type: 'warning',
        title: 'No Files Selected',
        message: 'Please upload at least one document to proceed with validation.'
      });
      return;
    }

    const requiredDocs = requiredDocuments.filter(doc => doc.required);
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
        user_type: 'exporter'
      });

      showToast({
        type: 'success',
        title: 'Validation Started',
        message: `Job ${result.job_id} created successfully. Redirecting to results...`
      });

      // Redirect to results page
      setTimeout(() => {
        navigate(`/exporter-results/${result.job_id}`);
      }, 1000);

    } catch (error) {
      showToast({
        type: 'error',
        title: 'Validation Failed',
        message: error instanceof Error ? error.message : 'An error occurred while starting validation.'
      });
    }
  };

  const allRequiredChecked = requiredDocuments
    .filter(doc => doc.required)
    .every(doc => checkedDocuments.includes(doc.id));

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/exporter-dashboard')}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Export LC Upload</h1>
          <p className="text-gray-600 mt-1">
            Upload your export documents for comprehensive validation and compliance checking
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Upload Area */}
          <div className="lg:col-span-2 space-y-8">
            {/* Document Upload */}
            <section className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Upload Documents
              </h2>

              <FileUploader
                onFilesSelect={handleFilesSelect}
                maxFiles={10}
                maxSize={25 * 1024 * 1024} // 25MB
                acceptedTypes={['.pdf', '.jpg', '.jpeg', '.png']}
                disabled={validateMutation.isPending}
              />

              {selectedFiles.length > 0 && (
                <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 text-green-800">
                    <CheckCircle size={16} />
                    <span className="text-sm font-medium">
                      {selectedFiles.length} documents ready for validation
                    </span>
                  </div>
                </div>
              )}
            </section>

            {/* Document Verification */}
            <section className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Document Verification Checklist
              </h2>
              <p className="text-sm text-gray-600 mb-6">
                Please confirm that you have uploaded the following documents:
              </p>

              <div className="space-y-4">
                {requiredDocuments.map((doc) => (
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
                        <h3 className="font-medium text-gray-900">{doc.name}</h3>
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
                  <h2 className="text-lg font-semibold text-gray-900">Ready to Validate</h2>
                  <p className="text-sm text-gray-600">
                    Validation typically takes 1-3 minutes
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">৳150</div>
                  <div className="text-sm text-gray-600">per validation</div>
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
                    Starting Validation...
                  </>
                ) : (
                  <>
                    <UploadIcon size={18} />
                    Start LC Validation
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
            {/* Process Overview */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Validation Process
              </h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    1
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Document Upload</div>
                    <div className="text-sm text-gray-600">Upload all required documents</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    2
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">AI Validation</div>
                    <div className="text-sm text-gray-600">Automated compliance checking</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    3
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Results & Actions</div>
                    <div className="text-sm text-gray-600">Review results and corrections</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    4
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Customs Package</div>
                    <div className="text-sm text-gray-600">Download ready documents</div>
                  </div>
                </div>
              </div>
            </section>

            {/* What We Check */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                What We Validate
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>LC clause compliance</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Document consistency</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Bangladesh Bank regulations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>UCP 600 standards</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Mathematical calculations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Date validations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Format requirements</span>
                </div>
              </div>
            </section>

            {/* Support */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Need Help?
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Having trouble with document uploads or validation requirements?
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
      </div>
    </div>
  );
};

export default ExportLCUpload;