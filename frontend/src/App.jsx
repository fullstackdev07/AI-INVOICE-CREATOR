// frontend/src/App.jsx
import React, { useState } from 'react';
import axios from 'axios';
import InvoiceEditor from './components/InvoiceEditor';

function App() {
  const [prompt, setPrompt] = useState('An invoice for a freelance graphic designer with tax');
  const [invoiceData, setInvoiceData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setIsLoading(true);
    setError('');
    setInvoiceData(null);
    try {
      const response = await axios.post(`https://ai-invoice-creator-1.onrender.com/api/generate-template?prompt=${encodeURIComponent(prompt)}`);
      setInvoiceData(response.data);
    } catch (error) {
      console.error("Error generating template:", error);
      setError("Failed to generate template. Please check the backend console and your API key.");
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <div className="container mx-auto p-4 sm:p-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-800">AI Invoice Creator</h1>
          <p className="text-gray-600 mt-2">Describe the invoice you need, and let AI do the rest.</p>
        </header>
        
        <div className="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow-md">
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-grow p-3 border rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="e.g., 'invoice for a construction company with tax'"
            />
            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-3 font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {isLoading ? 'Generating...' : '✨ Generate'}
            </button>
          </div>
          {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
        </div>

        {isLoading && (
          <div className="text-center py-10">
            <p className="text-lg text-gray-600">Generating your template, please wait...</p>
          </div>
        )}

        {invoiceData && (
          <div className="mt-8">
            <InvoiceEditor initialData={invoiceData} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;