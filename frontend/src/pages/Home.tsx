import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            NTAL Telehealth
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Inclusive, safe telehealth for everyone
          </p>
          <p className="text-gray-500">
            Via USSD/SMS/WhatsApp and offline-first CHW app
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
            <div className="text-center mb-6">
              <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Patient Triage
              </h2>
              <p className="text-gray-600 mb-6">
                Submit your symptoms and get help from a healthcare provider
              </p>
              <button
                onClick={() => navigate('/triage')}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Start Triage
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
            <div className="text-center mb-6">
              <div className="inline-block p-4 bg-green-100 rounded-full mb-4">
                <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Provider Portal
              </h2>
              <p className="text-gray-600 mb-6">
                Healthcare providers: Login to review and manage cases
              </p>
              <button
                onClick={() => navigate('/login')}
                className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Provider Login
              </button>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Access Channels</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="font-semibold text-gray-900">Web</p>
              <p className="text-sm text-gray-600">Online Portal</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="font-semibold text-gray-900">USSD</p>
              <p className="text-sm text-gray-600">Feature Phones</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="font-semibold text-gray-900">SMS</p>
              <p className="text-sm text-gray-600">Text Messages</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="font-semibold text-gray-900">WhatsApp</p>
              <p className="text-sm text-gray-600">Messaging App</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
