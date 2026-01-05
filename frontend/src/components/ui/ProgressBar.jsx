import React from 'react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

export const ProgressBar = ({ value = 0, max = 100, className, indicatorClassName, label }) => {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));

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
                    className={cn("h-full bg-primary transition-all duration-300 rounded-full", indicatorClassName)}
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ ease: "easeOut" }}
                />
            </div>
        </div>
    );
};
