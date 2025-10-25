import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const analyzeRepo = async (repo_url) => {
  const response = await axios.post(`${API_BASE}/analyze`, { repo_url });
  return response.data;
};
