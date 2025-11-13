import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { encounterService, callbackService } from '../services/api';
import type { Encounter, Callback } from '../types';
import { useAuth } from '../contexts/AuthContext';
import CallbackQueue from '../components/CallbackQueue';

const Dashboard: React.FC = () => {
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [callbacks, setCallbacks] = useState<Callback[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [view, setView] = useState<'encounters' | 'callbacks'>('encounters');
  const { provider, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [encountersData, callbacksData] = await Promise.all([
        encounterService.getAll(),
        callbackService.getAll()
      ]);
      setEncounters(encountersData);
      setCallbacks(callbacksData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignCallback = async (callbackId: number) => {
    if (!provider) return;
    await callbackService.assign(callbackId, { provider_id: provider.id });
  };

  const handleCompleteCallback = async (callbackId: number, outcome: string, notes?: string) => {
    await callbackService.complete(callbackId, { outcome, notes });
  };

  // Create encounter map for callback queue
  const encounterMap = new Map(encounters.map(e => [e.id, e]));

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
          
          {/* View Toggle */}
          <div className="flex space-x-2 mb-4">
            <button
              onClick={() => setView('encounters')}
              className={`px-6 py-2 rounded-lg font-medium ${
                view === 'encounters'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              All Encounters
            </button>
            <button
              onClick={() => setView('callbacks')}
              className={`px-6 py-2 rounded-lg font-medium ${
                view === 'callbacks'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              USSD Callbacks
              {callbacks.filter(cb => cb.status === 'queued').length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-red-500 text-white rounded-full text-xs">
                  {callbacks.filter(cb => cb.status === 'queued').length}
                </span>
              )}
            </button>
          </div>

          {/* Encounter Filters (only show when viewing encounters) */}
          {view === 'encounters' && (
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
          )}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        ) : view === 'callbacks' ? (
          <CallbackQueue
            callbacks={callbacks}
            encounters={encounterMap}
            providerId={provider?.id || 0}
            onAssign={handleAssignCallback}
            onComplete={handleCompleteCallback}
            onRefresh={loadData}
          />
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
                        {encounter.patient_name || `Case #${encounter.id}`}
                        {encounter.channel === 'USSD' && (
                          <span className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                            USSD
                          </span>
                        )}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Case #{encounter.id}
                        {encounter.patient_phone && ` • ${encounter.patient_phone}`}
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
                    {encounter.chief_complaint ? (
                      <>
                        <p className="text-sm font-medium text-gray-700">Chief Complaint:</p>
                        <p className="text-gray-900">{encounter.chief_complaint}</p>
                      </>
                    ) : encounter.risk_code ? (
                      <>
                        <p className="text-sm font-medium text-gray-700">Risk Assessment:</p>
                        <p className="text-gray-900">{encounter.risk_code.replace('_', ' ')}</p>
                      </>
                    ) : null}
                  </div>

                  {encounter.symptoms && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700">Symptoms:</p>
                      <p className="text-gray-600 text-sm">{encounter.symptoms}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500 pt-3 border-t">
                    <span>Source: {encounter.channel || encounter.source}</span>
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
