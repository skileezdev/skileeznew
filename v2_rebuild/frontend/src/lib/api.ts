import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor for token
api.interceptors.request.use(
    (config) => {
        const token = typeof window !== "undefined" ? localStorage.getItem("skileez_token") : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Backward compatibility wrapper for fetch
export const apiFetch = async (endpoint: string, options: any = {}) => {
    const res = await api({
        url: endpoint,
        method: options.method || "GET",
        data: options.body ? JSON.parse(options.body) : undefined,
        ...options
    });
    return res.data;
};

export default api;
