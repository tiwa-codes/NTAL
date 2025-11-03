import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { encounterService } from '../services/api';
import type { Encounter } from '../types';
import { useAuth } from '../contexts/AuthContext';

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [encounter, setEncounter] = useState<Encounter | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState('');
  const [urgency, setUrgency] = useState('');
  const [updating, setUpdating] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadEncounter();
  }, [id]);

  const loadEncounter = async () => {
    try {
      const data = await encounterService.getById(Number(id));
      setEncounter(data);
      setNotes(data.notes || '');
      setStatus(data.status);
      setUrgency(data.urgency);
    } catch (error) {
      console.error('Failed to load encounter:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!encounter) return;
    
    setUpdating(true);
    try {
      const updated = await encounterService.update(encounter.id, {
        notes,
        status: status as any,
        urgency: urgency as any,
      });
      setEncounter(updated);
      alert('Case updated successfully!');
    } catch (error) {
      alert('Failed to update case');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading case details...</p>
        </div>
      </div>
    );
  }

  if (!encounter) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Case not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <h1 className="text-xl font-bold text-gray-900">NTAL Telehealth</h1>
            </div>
            <div className="flex items-center">
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

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="bg-blue-600 px-6 py-4">
            <h2 className="text-2xl font-bold text-white">Case #{encounter.id}</h2>
            <p className="text-blue-100">Patient: {encounter.patient_name}</p>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Patient Information</h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                    <dd className="text-gray-900">{encounter.patient_name}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Phone</dt>
                    <dd className="text-gray-900">{encounter.patient_phone}</dd>
                  </div>
                  {encounter.patient_age && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Age</dt>
                      <dd className="text-gray-900">{encounter.patient_age} years</dd>
                    </div>
                  )}
                  {encounter.patient_gender && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Gender</dt>
                      <dd className="text-gray-900 capitalize">{encounter.patient_gender}</dd>
                    </div>
                  )}
                </dl>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Case Information</h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Source</dt>
                    <dd className="text-gray-900 uppercase">{encounter.source}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Submitted</dt>
                    <dd className="text-gray-900">
                      {new Date(encounter.created_at).toLocaleString()}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                    <dd className="text-gray-900">
                      {new Date(encounter.updated_at).toLocaleString()}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Chief Complaint</h3>
              <p className="text-gray-900 bg-gray-50 p-4 rounded">{encounter.chief_complaint}</p>
            </div>

            {encounter.symptoms && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Symptoms</h3>
                <p className="text-gray-900 bg-gray-50 p-4 rounded">{encounter.symptoms}</p>
              </div>
            )}

            {encounter.duration && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Duration</h3>
                <p className="text-gray-900 bg-gray-50 p-4 rounded">{encounter.duration}</p>
              </div>
            )}

            {encounter.medical_history && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Medical History</h3>
                <p className="text-gray-900 bg-gray-50 p-4 rounded">{encounter.medical_history}</p>
              </div>
            )}

            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Provider Actions</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Urgency
                  </label>
                  <select
                    value={urgency}
                    onChange={(e) => setUrgency(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Provider Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add notes, diagnosis, treatment plan, etc."
                />
              </div>

              <button
                onClick={handleUpdate}
                disabled={updating}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 font-medium"
              >
                {updating ? 'Updating...' : 'Update Case'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;
