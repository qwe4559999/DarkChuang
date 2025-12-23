import { auth } from '../stores/auth';
import { get } from 'svelte/store';

const API_BASE_URL = '/api/v1';
const AUTH_BASE_URL = '/api/auth';

export type MessageRole = 'user' | 'assistant';
export type MessageType = 'text' | 'image' | 'molecule';

export interface Message {
    role: MessageRole;
    content: string;
    type?: MessageType;
    data?: any; // For molecule properties, images, etc.
}

function getHeaders(contentType: string = 'application/json'): HeadersInit {
    const headers: HeadersInit = {};
    if (contentType) {
        headers['Content-Type'] = contentType;
    }
    const token = get(auth).token;
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

function getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {};
    const token = get(auth).token;
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

export const api = {
    async login(email: string, password: string): Promise<any> {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${AUTH_BASE_URL}/login/access-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });
        if (!response.ok) throw new Error('Login failed');
        return response.json();
    },

    async register(email: string, password: string, fullName?: string): Promise<any> {
        const response = await fetch(`${AUTH_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, full_name: fullName }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
        return response.json();
    },

    async getMe(): Promise<any> {
        const response = await fetch(`${AUTH_BASE_URL}/me`, {
            method: 'GET',
            headers: getHeaders(),
        });
        if (!response.ok) throw new Error('Failed to fetch user info');
        return response.json();
    },

    async uploadImage(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/upload/image`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload image');
        return response.json();
    },

    async sendMessage(message: string, imagePath?: string, conversationId?: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ 
                message, 
                use_rag: true,
                image_path: imagePath,
                conversation_id: conversationId
            }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    },

    async calculateProperties(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/calculate-properties`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ molecule }),
        });
        if (!response.ok) throw new Error('Failed to calculate properties');
        return response.json();
    },

    async generateStructure(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/structure-image`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ molecule }),
        });
        if (!response.ok) throw new Error('Failed to generate structure');
        return response.json();
    },

    async generate3DStructure(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/structure-3d`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ molecule }),
        });
        if (!response.ok) throw new Error('Failed to generate 3D structure');
        return response.json();
    },

    async uploadSpectrum(file: File, type: string = 'auto', additionalInfo: string = ''): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('spectrum_type', type);
        if (additionalInfo) formData.append('additional_info', additionalInfo);

        const response = await fetch(`${API_BASE_URL}/spectrum/analyze`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData,
        });

        if (!response.ok) {
            let errorMsg = 'Failed to analyze spectrum';
            try {
                const errorData = await response.json();
                if (errorData.detail) errorMsg += `: ${errorData.detail}`;
            } catch (e) {
                // Ignore json parse error
            }
            throw new Error(errorMsg);
        }
        return response.json();
    },

    async getChatHistory(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat/history`, {
            method: 'GET',
            headers: getHeaders(),
        });
        if (!response.ok) throw new Error('Failed to fetch history');
        return response.json();
    },

    async getConversation(id: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat/history/${id}`, {
            method: 'GET',
            headers: getHeaders(),
        });
        if (!response.ok) throw new Error('Failed to fetch conversation');
        return response.json();
    },

    async deleteConversation(id: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat/history/${id}`, {
            method: 'DELETE',
            headers: getHeaders(),
        });
        if (!response.ok) throw new Error('Failed to delete conversation');
        return response.json();
    },

    async uploadDocuments(files: File[]): Promise<any> {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const response = await fetch(`${API_BASE_URL}/knowledge/upload`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData,
        });

        if (!response.ok) throw new Error('Failed to upload documents');
        return response.json();
    },

    async getKnowledgeFiles(): Promise<any[]> {
        const response = await fetch(`${API_BASE_URL}/knowledge/files`, {
            headers: getHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch knowledge files');
        return response.json();
    },

    async deleteKnowledgeFile(fileId: number): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/files/${fileId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        if (!response.ok) throw new Error('Failed to delete file');
        return response.json();
    },

    async resetKnowledgeBase(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/reset`, {
            method: 'POST',
            headers: getHeaders()
        });
        if (!response.ok) throw new Error('Failed to reset knowledge base');
        return response.json();
    },

    async getKnowledgeBaseStats(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/stats`, {
            headers: getHeaders()
        });
        if (!response.ok) throw new Error('Failed to get stats');
        return response.json();
    }
};
