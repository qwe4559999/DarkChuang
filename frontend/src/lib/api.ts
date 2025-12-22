const API_BASE_URL = 'http://localhost:8000/api/v1';

export type MessageRole = 'user' | 'assistant';
export type MessageType = 'text' | 'image' | 'molecule';

export interface Message {
    role: MessageRole;
    content: string;
    type?: MessageType;
    data?: any; // For molecule properties, images, etc.
}

export const api = {
    async sendMessage(message: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, use_rag: true }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    },

    async calculateProperties(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/calculate-properties`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ molecule }),
        });
        if (!response.ok) throw new Error('Failed to calculate properties');
        return response.json();
    },

    async generateStructure(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/structure-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ molecule }),
        });
        if (!response.ok) throw new Error('Failed to generate structure');
        return response.json();
    },

    async uploadSpectrum(file: File, type: string = 'auto', additionalInfo: string = ''): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('spectrum_type', type);
        if (additionalInfo) formData.append('additional_info', additionalInfo);

        const response = await fetch(`${API_BASE_URL}/spectrum/analyze`, {
            method: 'POST',
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

    async uploadDocuments(files: File[]): Promise<any> {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const response = await fetch(`${API_BASE_URL}/knowledge/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error('Failed to upload documents');
        return response.json();
    },

    async getKnowledgeBaseStats(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/stats`);
        if (!response.ok) throw new Error('Failed to get stats');
        return response.json();
    }
};
