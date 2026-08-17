import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Config {
  [channel: string]: {
    engine: string;
    voice: string;
  };
}

export interface SynthesisResponse {
  url: string;
}

export const fetchConfig = async (): Promise<Config> => {
  const response = await axios.get(`${API_BASE_URL}/config`);
  return response.data;
};

export const synthesize = async (
  text: string,
  engine?: string,
  voice?: string,
  channel?: string
): Promise<SynthesisResponse> => {
  const response = await axios.post(`${API_BASE_URL}/synthesize`, {
    text,
    engine,
    voice,
    channel,
  });
  return response.data;
};

export const getAudioUrl = (url: string) => `${API_BASE_URL}${url}`;
