import React, { useEffect, useState } from 'react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

/**
 * ProgressBar
 *
 * - Determinate mode: pass an explicit `value` (0–max)
 * - Auto-progress mode: pass `isActive` when backend only sends 0 → 100;
 *   the bar will smoothly move towards ~90% while active, then jump to 100%
 *   when `value` reaches max.
 */
export const ProgressBar = ({
    value = 0,
    max = 100,
    className,
    indicatorClassName,
    label,
    isActive = false,
}) => {
    const [displayValue, setDisplayValue] = useState(value);

    // Smooth, optimistic auto-progress when only 0 and 100 are known
    useEffect(() => {
        // If we've hit max or we're not active, snap to the real value
        if (!isActive || value >= max) {
            setDisplayValue(value);
            return;
        }

        // While active and not complete, gently move towards ~90%
        const targetCap = max * 0.9;
        const interval = setInterval(() => {
            setDisplayValue((current) => {
                // If backend started giving us an intermediate real value, respect it
                const baseline = Math.max(current, value);
                if (baseline >= targetCap) return baseline;
                // Increment by a small random step for a natural feel
                const step = Math.random() * 5 + 1; // 1–6%
                return Math.min(targetCap, baseline + step);
            });
        }, 500);

        return () => clearInterval(interval);
    }, [isActive, value, max]);

    // When value jumps to max, immediately show completion
    useEffect(() => {
        if (value >= max) {
            setDisplayValue(max);
        }
    }, [value, max]);

    const percentage = Math.min(100, Math.max(0, (displayValue / max) * 100));

    return (
        <div className={cn("w-full", className)}>
            {label && (
                <div className="flex justify-between text-xs mb-1 text-muted-foreground">
                    <span>{label}</span>
                    <span>{Math.round(percentage)}%</span>
                </div>
            )}
            <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <motion.div
                    className={cn(
                        "h-full bg-primary rounded-full",
                        "transition-[width] duration-300 ease-out",
                        indicatorClassName
                    )}
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
};
