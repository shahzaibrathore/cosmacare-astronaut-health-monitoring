
import React, { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8081';

function App() {
  const [crew, setCrew] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [telemetry, setTelemetry] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    crew_id: '',
    heart_rate: '75',
    spo2: '98',
    body_temp: '37',
    systolic_bp: '120',
    diastolic_bp: '80'
  });

  // Load dashboard data from backend
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      const crewResponse = await fetch(`${API_BASE}/crew/`);

      if (!crewResponse.ok) {
        throw new Error('Could not load crew members');
      }

      const crewData = await crewResponse.json();
      setCrew(crewData);

      const alertResponse = await fetch(`${API_BASE}/alerts/?limit=100`);

      if (!alertResponse.ok) {
        throw new Error('Could not load alerts');
      }

      const alertData = await alertResponse.json();
      setAlerts(alertData);

      let allTelemetry = [];

      for (const member of crewData) {
        const response = await fetch(
          `${API_BASE}/telemetry/${member.id}?limit=50`
        );

        if (response.ok) {
          const records = await response.json();
          allTelemetry = [...allTelemetry, ...records];
        }
      }

      allTelemetry.sort(
        (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
      );

      setTelemetry(allTelemetry);

      if (crewData.length > 0) {
        setFormData(previous => ({
          ...previous,
          crew_id: String(crewData[0].id)
        }));
      }
    } catch (err) {
      setError(
        'Backend connection failed. Make sure Uvicorn is running on port 8081.'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Handle input changes
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData(previous => ({
      ...previous,
      [name]: value
    }));
  };

  // Submit telemetry to backend
  const handleTelemetrySubmit = async (event) => {
    event.preventDefault();

    setMessage('');
    setError('');

    const payload = {
      crew_id: Number(formData.crew_id),
      heart_rate: Number(formData.heart_rate),
      spo2: Number(formData.spo2),
      body_temp: Number(formData.body_temp),
      systolic_bp: Number(formData.systolic_bp),
      diastolic_bp: Number(formData.diastolic_bp)
    };

    try {
      const response = await fetch(`${API_BASE}/telemetry/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail
            ? JSON.stringify(result.detail)
            : 'Telemetry submission failed'
        );
      }

      setMessage('Telemetry submitted successfully!');

      await loadDashboardData();
    } catch (err) {
      setError(err.message);
      console.error(err);
    }
  };

  // Acknowledge alert
  const acknowledgeAlert = async (alertId) => {
    try {
      const response = await fetch(
        `${API_BASE}/alerts/${alertId}/acknowledge`,
        {
          method: 'POST'
        }
      );

      if (!response.ok) {
        throw new Error('Could not acknowledge alert');
      }

      setMessage('Alert acknowledged successfully!');
      await loadDashboardData();
    } catch (err) {
      setError(err.message);
    }
  };

  const criticalAlerts = alerts.filter(
    alert =>
      String(alert.severity).toLowerCase() === 'critical' &&
      !alert.acknowledged
  );

  const openAlerts = alerts.filter(
    alert => !alert.acknowledged
  );

  const latestTelemetry = telemetry[0];

  const getSeverityColor = (severity) => {
    const value = String(severity).toLowerCase();

    if (value === 'critical') return 'text-red-400 bg-red-500/10';
    if (value === 'warning') return 'text-yellow-400 bg-yellow-500/10';

    return 'text-blue-400 bg-blue-500/10';
  };

  const formatDate = (date) => {
    if (!date) return 'N/A';

    return new Date(date).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-[#080d18] text-white">

      {/* Header */}
      <header className="border-b border-slate-800 bg-[#0d1423] px-6 py-5">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-wide text-cyan-400">
              COSMACARE
            </h1>
            <p className="text-sm text-slate-400">
              Astronaut Health Monitoring System
            </p>
          </div>

          <button
            onClick={loadDashboardData}
            className="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold hover:bg-cyan-500"
          >
            Refresh Data
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">

        {/* Status */}
        <section className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">
              Mission Dashboard
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Live data from the CosmaCare backend
            </p>
          </div>

          <span className="rounded-full bg-green-500/10 px-4 py-2 text-sm text-green-400">
            ● Monitoring System
          </span>
        </section>

        {/* Messages */}
        {loading && (
          <p className="rounded-lg bg-blue-500/10 p-4 text-blue-300">
            Loading dashboard data...
          </p>
        )}

        {error && (
          <p className="rounded-lg bg-red-500/10 p-4 text-red-300">
            {error}
          </p>
        )}

        {message && (
          <p className="rounded-lg bg-green-500/10 p-4 text-green-300">
            {message}
          </p>
        )}

        {/* Dashboard Cards */}
        <section className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border border-slate-800 bg-[#111c2e] p-5">
            <p className="text-sm text-slate-400">Crew Members</p>
            <h3 className="mt-3 text-3xl font-bold text-cyan-400">
              {crew.length}
            </h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#111c2e] p-5">
            <p className="text-sm text-slate-400">Critical Alerts</p>
            <h3 className="mt-3 text-3xl font-bold text-red-400">
              {criticalAlerts.length}
            </h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#111c2e] p-5">
            <p className="text-sm text-slate-400">Telemetry Records</p>
            <h3 className="mt-3 text-3xl font-bold text-green-400">
              {telemetry.length}
            </h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#111c2e] p-5">
            <p className="text-sm text-slate-400">Open Alerts</p>
            <h3 className="mt-3 text-3xl font-bold text-yellow-400">
              {openAlerts.length}
            </h3>
          </div>

        </section>

        {/* Latest Telemetry */}
        <section className="rounded-xl border border-slate-800 bg-[#111c2e] p-6">
          <h2 className="mb-5 text-xl font-bold">
            Latest Telemetry
          </h2>

          {latestTelemetry ? (
            <div className="grid grid-cols-2 gap-5 md:grid-cols-3 lg:grid-cols-6">

              <div>
                <p className="text-sm text-slate-400">Heart Rate</p>
                <p className="mt-2 text-2xl font-bold text-red-400">
                  {latestTelemetry.heart_rate} bpm
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">SpO2</p>
                <p className="mt-2 text-2xl font-bold text-cyan-400">
                  {latestTelemetry.spo2}%
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Temperature</p>
                <p className="mt-2 text-2xl font-bold text-yellow-400">
                  {latestTelemetry.body_temp}°C
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Systolic BP</p>
                <p className="mt-2 text-2xl font-bold">
                  {latestTelemetry.systolic_bp}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Diastolic BP</p>
                <p className="mt-2 text-2xl font-bold">
                  {latestTelemetry.diastolic_bp}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-400">Crew ID</p>
                <p className="mt-2 text-2xl font-bold">
                  {latestTelemetry.crew_id}
                </p>
              </div>

            </div>
          ) : (
            <p className="text-slate-400">
              No telemetry records available yet.
            </p>
          )}
        </section>

        {/* Crew Members */}
        <section className="rounded-xl border border-slate-800 bg-[#111c2e] p-6">
          <h2 className="mb-5 text-xl font-bold">
            Crew Members
          </h2>

          {crew.length === 0 ? (
            <p className="text-slate-400">
              No crew members found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-700 text-slate-400">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Name</th>
                    <th className="p-3">Role</th>
                  </tr>
                </thead>

                <tbody>
                  {crew.map(member => (
                    <tr
                      key={member.id}
                      className="border-b border-slate-800"
                    >
                      <td className="p-3">{member.id}</td>
                      <td className="p-3 font-semibold">
                        {member.name}
                      </td>
                      <td className="p-3 text-slate-400">
                        {member.role || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Telemetry Form */}
        <section className="rounded-xl border border-slate-800 bg-[#111c2e] p-6">
          <h2 className="mb-2 text-xl font-bold">
            Submit Health Telemetry
          </h2>

          <p className="mb-6 text-sm text-slate-400">
            Enter crew health measurements to send them to the backend.
          </p>

          <form
            onSubmit={handleTelemetrySubmit}
            className="grid grid-cols-1 gap-5 md:grid-cols-2"
          >

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Crew Member
              </label>

              <select
                name="crew_id"
                value={formData.crew_id}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              >
                <option value="">Select crew member</option>

                {crew.map(member => (
                  <option key={member.id} value={member.id}>
                    {member.name} (ID: {member.id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Heart Rate (bpm)
              </label>

              <input
                type="number"
                name="heart_rate"
                min="30"
                max="220"
                value={formData.heart_rate}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Oxygen Saturation (SpO2 %)
              </label>

              <input
                type="number"
                name="spo2"
                min="50"
                max="100"
                step="0.1"
                value={formData.spo2}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Body Temperature (°C)
              </label>

              <input
                type="number"
                name="body_temp"
                min="30"
                max="43"
                step="0.1"
                value={formData.body_temp}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Systolic Blood Pressure
              </label>

              <input
                type="number"
                name="systolic_bp"
                min="60"
                max="250"
                value={formData.systolic_bp}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">
                Diastolic Blood Pressure
              </label>

              <input
                type="number"
                name="diastolic_bp"
                min="40"
                max="150"
                value={formData.diastolic_bp}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] p-3 text-white"
              />
            </div>

            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={loading || crew.length === 0}
                className="w-full rounded-lg bg-cyan-600 px-5 py-3 font-bold text-white hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Submit Telemetry
              </button>
            </div>

          </form>
        </section>

        {/* Alerts */}
        <section className="rounded-xl border border-slate-800 bg-[#111c2e] p-6">
          <h2 className="mb-5 text-xl font-bold">
            Health Alerts
          </h2>

          {alerts.length === 0 ? (
            <p className="text-slate-400">
              No alerts available.
            </p>
          ) : (
            <div className="space-y-4">

              {alerts.map(alert => (
                <div
                  key={alert.id}
                  className="flex flex-col justify-between gap-4 rounded-lg border border-slate-700 p-4 md:flex-row md:items-center"
                >

                  <div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold uppercase ${getSeverityColor(alert.severity)}`}
                    >
                      {alert.severity}
                    </span>

                    <p className="mt-3 font-semibold">
                      {alert.message}
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      Crew ID: {alert.crew_id} |
                      {' '}{formatDate(alert.timestamp)}
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      Status: {alert.acknowledged ? 'Acknowledged' : 'Open'}
                    </p>
                  </div>

                  {!alert.acknowledged && (
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold hover:bg-cyan-500"
                    >
                      Acknowledge
                    </button>
                  )}

                </div>
              ))}

            </div>
          )}
        </section>

        {/* Telemetry History */}
        <section className="rounded-xl border border-slate-800 bg-[#111c2e] p-6">
          <h2 className="mb-5 text-xl font-bold">
            Telemetry History
          </h2>

          {telemetry.length === 0 ? (
            <p className="text-slate-400">
              No telemetry history available.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-700 text-slate-400">
                  <tr>
                    <th className="p-3">Crew ID</th>
                    <th className="p-3">Heart Rate</th>
                    <th className="p-3">SpO2</th>
                    <th className="p-3">Temperature</th>
                    <th className="p-3">Blood Pressure</th>
                    <th className="p-3">Time</th>
                  </tr>
                </thead>

                <tbody>
                  {telemetry.map(record => (
                    <tr
                      key={record.id}
                      className="border-b border-slate-800"
                    >
                      <td className="p-3">{record.crew_id}</td>
                      <td className="p-3">{record.heart_rate} bpm</td>
                      <td className="p-3">{record.spo2}%</td>
                      <td className="p-3">{record.body_temp}°C</td>
                      <td className="p-3">
                        {record.systolic_bp}/{record.diastolic_bp}
                      </td>
                      <td className="p-3 text-slate-400">
                        {formatDate(record.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

      </main>

      <footer className="border-t border-slate-800 px-6 py-5 text-center text-sm text-slate-500">
        CosmaCare | Astronaut Health Monitoring System
      </footer>

    </div>
  );
}

export default App;
