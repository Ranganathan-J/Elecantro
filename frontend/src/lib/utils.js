import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges class names safely with Tailwind conflict resolution
 */
export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
}

export function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    });
}
