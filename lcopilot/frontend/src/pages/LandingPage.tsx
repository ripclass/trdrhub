import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCheck,
  Upload,
  Shield,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Star,
  Users,
  Clock,
  DollarSign
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleRoleSelection = (role: 'exporter' | 'importer') => {
    if (role === 'exporter') {
      navigate('/exporter-dashboard');
    } else {
      navigate('/importer-dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-green-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <div className="flex items-center gap-3">
                <FileCheck size={48} className="text-green-500" />
                <h1 className="text-4xl font-bold text-gray-900">LCopilot</h1>
              </div>
            </div>

            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Streamline Your<br />
              <span className="text-green-600">Trade Documentation</span>
            </h2>

            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Automated LC validation, compliance checking, and document preparation
              for Bangladeshi SMEs. Reduce processing time from days to minutes.
            </p>

            {/* Role Selection CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button
                onClick={() => handleRoleSelection('exporter')}
                className="w-full sm:w-auto bg-green-500 hover:bg-green-600 text-white font-semibold px-8 py-4 rounded-lg transition-colors flex items-center justify-center gap-2 min-w-64"
              >
                <Upload size={24} />
                I'm an Exporter
                <ArrowRight size={20} />
              </button>

              <button
                onClick={() => handleRoleSelection('importer')}
                className="w-full sm:w-auto bg-blue-500 hover:bg-blue-600 text-white font-semibold px-8 py-4 rounded-lg transition-colors flex items-center justify-center gap-2 min-w-64"
              >
                <Shield size={24} />
                I'm an Importer
                <ArrowRight size={20} />
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>500+ SMEs served</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>99.7% accuracy rate</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>24/7 support</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose LCopilot?
            </h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built specifically for Bangladeshi trade requirements with deep understanding
              of local banking and customs procedures.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                <Clock size={24} className="text-green-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">
                Lightning Fast Processing
              </h4>
              <p className="text-gray-600 mb-4">
                Validate LC documents in under 2 minutes. Get instant compliance
                reports and actionable recommendations.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Automated clause analysis</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Real-time validation</span>
                </li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <Shield size={24} className="text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">
                Compliance Guaranteed
              </h4>
              <p className="text-gray-600 mb-4">
                Stay compliant with Bangladesh Bank regulations and international
                trade standards. Reduce rejection rates by 90%.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>BB compliance check</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>UCP 600 validation</span>
                </li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                <DollarSign size={24} className="text-green-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">
                Cost Effective
              </h4>
              <p className="text-gray-600 mb-4">
                Save up to 80% on documentation costs. Eliminate expensive
                amendments and reduce processing delays.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>Pay per validation</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span>No monthly fees</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Trusted by Leading Exporters
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-gray-50 p-8 rounded-xl">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={16} className="text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "LCopilot reduced our document processing time from 3 days to 30 minutes.
                The compliance checks have saved us thousands in amendment fees."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Users size={20} className="text-green-600" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Rashid Ahmed</div>
                  <div className="text-sm text-gray-600">Managing Director, Bengal Textiles</div>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-gray-50 p-8 rounded-xl">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={16} className="text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "The risk analysis feature helped us identify problematic clauses
                before signing the LC. Invaluable for import planning."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users size={20} className="text-blue-600" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Fatima Khan</div>
                  <div className="text-sm text-gray-600">Import Manager, Dhaka Trading Co.</div>
                </div>
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="bg-gray-50 p-8 rounded-xl">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={16} className="text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "Simple, fast, and accurate. LCopilot has become an essential part
                of our export operations. Highly recommended!"
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Users size={20} className="text-green-600" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Mohammad Hassan</div>
                  <div className="text-sm text-gray-600">CEO, Chittagong Exports Ltd.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Preview */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h3>
          <p className="text-xl text-gray-600 mb-8">
            Pay only for what you use. No setup fees, no monthly commitments.
          </p>

          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 max-w-md mx-auto">
            <div className="text-4xl font-bold text-gray-900 mb-2">৳150</div>
            <div className="text-gray-600 mb-6">per LC validation</div>

            <ul className="space-y-3 text-left text-gray-600 mb-8">
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>Complete compliance check</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>Risk analysis report</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>Customs-ready documentation</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" />
                <span>24/7 email support</span>
              </li>
            </ul>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => handleRoleSelection('exporter')}
                className="btn-primary flex-1"
              >
                Start as Exporter
              </button>
              <button
                onClick={() => handleRoleSelection('importer')}
                className="btn-secondary flex-1"
              >
                Start as Importer
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <FileCheck size={24} className="text-green-400" />
                <span className="text-xl font-bold">LCopilot</span>
              </div>
              <p className="text-gray-400 mb-4">
                Streamlining trade documentation for Bangladeshi SMEs with
                AI-powered compliance checking and validation.
              </p>
              <p className="text-sm text-gray-500">
                © 2024 LCopilot. All rights reserved.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API Documentation</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">System Status</a></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};


export default LandingPage;