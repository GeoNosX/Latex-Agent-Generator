import { useState } from 'react';
import { aiApi } from './api';

function App() {
  // --- STATE ---
  const [appStatus, setAppStatus] = useState('idle'); // idle, loading, review, completed, error
  const [prompt, setPrompt] = useState('');
  const [threadId] = useState(() => `session-${Math.random().toString(36).substr(2, 9)}`);
  const [exercises, setExercises] = useState([]);
  const [feedback, setFeedback] = useState('');
  const [latexCode, setLatexCode] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [pdfTimestamp, setPdfTimestamp] = useState(Date.now());

  // --- ACTIONS ---
  const handleGenerate = async () => {
    if (!prompt) return;
    setAppStatus('loading');
    setErrorMessage('');
    try {
      const data = await aiApi.generateDraft(prompt, threadId);
      if (data.status === 'paused_for_review') {
        setExercises(data.exercises);
        setPdfTimestamp(Date.now());
        setAppStatus('review');
      }
    } catch (error) {
      setErrorMessage(error.response?.data?.detail || 'Failed to generate draft.');
      setAppStatus('error');
    }
  };

  const handleResume = async (isApproved) => {
    setAppStatus('loading');
    setErrorMessage('');
    try {
      // Send approval status, feedback text, and the current exercises
      const data = await aiApi.resumeDraft(threadId, isApproved, feedback, exercises);
      
      if (data.status === 'paused_for_review') {
        setExercises(data.exercises);
        setFeedback(''); // Clear the feedback box for the next round
        setPdfTimestamp(Date.now());
        setAppStatus('review');
      } else if (data.status === 'completed') {
        setLatexCode(data.latex_code);
        setAppStatus('completed');
      }
    } catch (error) {
      setErrorMessage(error.response?.data?.detail || 'Failed to communicate with AI.');
      setAppStatus('error');
    }
  };

  // --- UI RENDERERS ---
  return (
    <div style={{ padding: '40px', maxWidth: '900px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px' }}>LaTeX AI Architect 🤖</h1>
      
      {/* 1. IDLE STATE: Ask for the prompt */}
      {appStatus === 'idle' && (
        <div style={{ marginTop: '20px' }}>
          <h3>What kind of exam do you want to build?</h3>
          <textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Create 2 simple physics word problems about falling apples."
            style={{ width: '100%', height: '100px', padding: '10px', marginBottom: '10px' }}
          />
          <button onClick={handleGenerate} style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
            Generate Draft
          </button>
        </div>
      )}

      {/* 2. LOADING STATE */}
      {appStatus === 'loading' && (
        <div style={{ marginTop: '40px', textAlign: 'center', color: '#666' }}>
          <h3>⏳ The AI is writing and compiling the LaTeX... please wait.</h3>
        </div>
      )}

      {/* 3. REVIEW STATE: Human-in-the-Loop (Live PDF Layout) */}
      {appStatus === 'review' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px', marginTop: '30px' }}>
          
          {/* TOP: The Control Panel (Chat & Actions) */}
          <div style={{ 
            backgroundColor: '#2d3748', 
            padding: '25px', 
            borderRadius: '8px',
            width: '100%',
            boxSizing: 'border-box'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
              <div style={{ flex: '1', minWidth: '300px' }}>
                <h3 style={{ color: '#d97706', margin: '0 0 10px 0' }}>🛑 Human Review</h3>
                <p style={{ color: '#cbd5e0', fontSize: '14px', margin: 0 }}>
                  Review the compiled PDF below. Request changes to re-draft, or approve to finish.
                </p>
                <textarea 
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="e.g., Change question 1 to be about a watermelon..."
                  style={{ 
                    width: '100%', 
                    height: '80px', 
                    padding: '12px', 
                    marginTop: '15px',
                    borderRadius: '6px', 
                    border: '1px solid #4a5568',
                    backgroundColor: '#1a202c',
                    color: '#e2e8f0',
                    fontFamily: 'monospace',
                    resize: 'vertical',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', minWidth: '250px' }}>
                <button 
                  onClick={() => handleResume(false)} 
                  style={{ padding: '12px', cursor: 'pointer', backgroundColor: '#4a5568', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold' }}>
                  🔄 Ask AI to Update Draft
                </button>
                <button 
                  onClick={() => handleResume(true)} 
                  style={{ padding: '12px', cursor: 'pointer', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', fontWeight: 'bold' }}>
                  ✅ Approve & Finish
                </button>
              </div>
            </div>
          </div>

          {/* BOTTOM: The REAL LaTeX PDF Viewer */}
          <div style={{ 
            backgroundColor: '#1e1e1e', 
            padding: '20px',
            borderRadius: '8px',
            height: '800px', // Fixed height for the PDF viewer
            width: '100%',
            boxSizing: 'border-box'
          }}>
            {/* We use Date.now() to trick the browser into bypassing its cache. 
              Otherwise, it will keep showing the old PDF even after the AI updates it!
            */}
            <iframe 
              src={`http://127.0.0.1:8000/pdfs/latest_exam.pdf?t=${pdfTimestamp}`}
              title="Compiled LaTeX PDF"
              style={{ width: '100%', height: '100%', border: 'none', borderRadius: '4px', backgroundColor: 'white' }}
            />
          </div>

        </div>
      )}

      {/* 4. COMPLETED STATE */}
      {appStatus === 'completed' && (
        <div style={{ marginTop: '20px' }}>
          <h3 style={{ color: '#28a745' }}>🎉 Workflow Complete!</h3>
          <p>Your final PDF has been saved to your server.</p>
          <div style={{ backgroundColor: '#2d2d2d', color: '#f8f8f2', padding: '15px', borderRadius: '6px', overflowX: 'auto', maxHeight: '300px' }}>
            <pre><code>{latexCode}</code></pre>
          </div>
          <button onClick={() => window.location.reload()} style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
            Start New Session
          </button>
        </div>
      )}

      {/* ERROR STATE */}
      {appStatus === 'error' && (
        <div style={{ marginTop: '20px', color: 'red', backgroundColor: '#fde8e8', padding: '15px', borderRadius: '6px' }}>
          <h3>❌ Error</h3>
          <p>{errorMessage}</p>
          <button onClick={() => setAppStatus('idle')} style={{ marginTop: '10px' }}>Try Again</button>
        </div>
      )}
    </div>
  );
}

export default App;