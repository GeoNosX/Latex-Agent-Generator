import axios from 'axios';

// This matches your FastAPI address
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const aiApi = {
  // 1. Kick off the initial generation
  generateDraft: async (prompt, threadId) => {
    const response = await axios.post(`${API_BASE_URL}/generate`, {
      prompt: prompt,
      thread_id: threadId
    });
    return response.data;
  },

  // 2. Send human feedback or approval back to the AI
  resumeDraft: async (threadId, isApproved, feedback = null, exercises = null) => {
    // Build the dynamic payload based on what the user provided
    const payload = {
      thread_id: threadId,
      user_approved: isApproved,
    };
    
    if (feedback) payload.feedback = feedback;
    if (exercises) payload.exercises = exercises;

    const response = await axios.post(`${API_BASE_URL}/resume`, payload);
    return response.data;
  }
};