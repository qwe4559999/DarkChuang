const API_BASE_URL = '/api/v1';

export type MessageRole = 'user' | 'assistant';
export type MessageType = 'text' | 'image' | 'molecule';

export interface Message {
    role: MessageRole;
    content: string;
    type?: MessageType;
    data?: any; // For molecule properties, images, etc.
}

export const api = {
    async uploadImage(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/upload/image`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload image');
        return response.json();
    },

    async sendMessage(message: string, imagePath?: string, conversationId?: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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

    async generate3DStructure(molecule: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chemistry/structure-3d`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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

    async getKnowledgeFiles(): Promise<any[]> {
        const response = await fetch(`${API_BASE_URL}/knowledge/files`);
        if (!response.ok) throw new Error('Failed to fetch knowledge files');
        return response.json();
    },

    async deleteKnowledgeFile(fileId: number): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/files/${fileId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete file');
        return response.json();
    },

    async getChatHistory(): Promise<any[]> {
        const response = await fetch(`${API_BASE_URL}/chat/history`);
        if (!response.ok) throw new Error('Failed to fetch chat history');
        return response.json();
    },

    async getConversation(conversationId: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`);
        if (!response.ok) throw new Error('Failed to fetch conversation');
        return response.json();
    },

    async deleteConversation(conversationId: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete conversation');
        return response.json();
    },

    async resetKnowledgeBase(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/reset`, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Failed to reset knowledge base');
        return response.json();
    },

    async getKnowledgeBaseStats(): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/knowledge/stats`);
        if (!response.ok) throw new Error('Failed to get stats');
        return response.json();
    }
};
