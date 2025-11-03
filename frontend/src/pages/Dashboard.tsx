import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { encounterService } from '../services/api';
import type { Encounter } from '../types';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const { provider, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadEncounters();
  }, []);

  const loadEncounters = async () => {
    try {
      const data = await encounterService.getAll();
      setEncounters(data);
    } catch (error) {
      console.error('Failed to load encounters:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-purple-100 text-purple-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredEncounters = encounters.filter(encounter => {
    if (filter === 'all') return true;
    return encounter.status === filter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">NTAL Telehealth</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                {provider?.full_name} ({provider?.role})
              </span>
              <button
                onClick={logout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Provider Dashboard</h2>
          
          <div className="flex space-x-2 mb-4">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border'}`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('pending')}
              className={`px-4 py-2 rounded ${filter === 'pending' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border'}`}
            >
              Pending
            </button>
            <button
              onClick={() => setFilter('in_progress')}
              className={`px-4 py-2 rounded ${filter === 'in_progress' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border'}`}
            >
              In Progress
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={`px-4 py-2 rounded ${filter === 'completed' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border'}`}
            >
              Completed
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading encounters...</p>
          </div>
        ) : filteredEncounters.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">No encounters found.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredEncounters.map((encounter) => (
              <div
                key={encounter.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/encounters/${encounter.id}`)}
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {encounter.patient_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Case #{encounter.id} • {encounter.patient_phone}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getUrgencyColor(encounter.urgency)}`}>
                        {encounter.urgency.toUpperCase()}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(encounter.status)}`}>
                        {encounter.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-700">Chief Complaint:</p>
                    <p className="text-gray-900">{encounter.chief_complaint}</p>
                  </div>

                  {encounter.symptoms && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700">Symptoms:</p>
                      <p className="text-gray-600 text-sm">{encounter.symptoms}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500 pt-3 border-t">
                    <span>Source: {encounter.source}</span>
                    <span>
                      Submitted: {new Date(encounter.created_at).toLocaleDateString()} {new Date(encounter.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
