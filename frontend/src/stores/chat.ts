import { writable } from 'svelte/store';
import type { Message } from '../lib/api';

function createChatStore() {
    const { subscribe, update, set } = writable<Message[]>([]);

    return {
        subscribe,
        addMessage: (message: Message) => update(messages => [...messages, message]),
        updateLastMessage: (message: Message) => update(messages => {
            const newMessages = [...messages];
            newMessages[newMessages.length - 1] = message;
            return newMessages;
        }),
        clear: () => set([]),
        setMessages: (messages: Message[]) => set(messages)
    };
}

export const messages = createChatStore();
export const isLoading = writable(false);
