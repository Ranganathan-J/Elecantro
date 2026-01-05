import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { cn } from '../lib/utils';
import { AlertCircle, CheckCircle, Clock, Search, Filter } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

const Insights = () => {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('all'); // all, negative, high_urgency
    const [selectedEntity, setSelectedEntity] = useState(null);

    // 1. Fetch Entities
    const { data: entities } = useQuery({
        queryKey: ['entities'],
        queryFn: async () => {
            const res = await api.get('/api/data-ingestion/entities/');
            return res.data;
        },
        onSuccess: (data) => {
            const list = Array.isArray(data) ? data : data.results || [];
            if (list.length > 0 && !selectedEntity) {
                setSelectedEntity(list[0].id);
            }
        }
    });

    const entityList = Array.isArray(entities) ? entities : entities?.results || [];
    const effectiveId = selectedEntity || (entityList.length > 0 ? entityList[0].id : null);

    const { data: processedFeedbacks, isLoading } = useQuery({
        queryKey: ['processed-feedbacks', filter, effectiveId],
        queryFn: async () => {
            if (!effectiveId) return [];
            const params = { entity_id: effectiveId };
            if (filter === 'negative') params.sentiment = 'negative';
            if (filter === 'high_urgency') params.urgency = 'high'; // Assuming 'high' or 'critical'

            // Note: Use the array response handling safety we learned!
            const res = await api.get('/api/analysis/processed-feedbacks/', { params });
            return Array.isArray(res.data) ? res.data : res.data.results || [];
        },
        enabled: !!effectiveId
    });

    const filteredData = processedFeedbacks?.filter(item =>
        item.text_preview.toLowerCase().includes(search.toLowerCase()) ||
        item.topics.some(t => t.toLowerCase().includes(search.toLowerCase()))
    );

    const getSentimentColor = (sentiment) => {
        switch (sentiment) {
            case 'positive': return 'bg-green-500/10 text-green-500 border-green-500/20';
            case 'negative': return 'bg-red-500/10 text-red-500 border-red-500/20';
            default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
        }
    };

    const getUrgencyColor = (urgency) => {
        switch (urgency) {
            case 'critical': return 'text-red-500 font-bold';
            case 'high': return 'text-orange-500 font-semibold';
            default: return 'text-muted-foreground';
        }
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Insights Explorer</h1>
                    <p className="text-muted-foreground mt-1">Deep dive into AI-analyzed feedback.</p>
                </div>

                {/* Entity Selector */}
                <div className="flex items-center gap-3 bg-secondary/20 p-2 px-3 rounded-lg border border-border/50">
                    <span className="text-xs font-semibold uppercase text-muted-foreground">Entity:</span>
                    {entityList.length > 0 ? (
                        <select
                            className="bg-transparent border-none text-sm font-semibold focus:ring-0 cursor-pointer min-w-[120px]"
                            value={selectedEntity || effectiveId || ''}
                            onChange={(e) => setSelectedEntity(e.target.value)}
                        >
                            {entityList.map(ent => (
                                <option key={ent.id} value={ent.id} className="bg-background">{ent.name}</option>
                            ))}
                        </select>
                    ) : (
                        <span className="text-xs text-yellow-500">No Entities</span>
                    )}
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 items-center bg-secondary/20 p-4 rounded-lg border border-border/50">
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
                    <Input
                        placeholder="Search text or topics..."
                        className="pl-9"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <div className="flex gap-2 w-full md:w-auto overflow-x-auto">
                    {['all', 'negative', 'high_urgency'].map(f => (
                        <Button
                            key={f}
                            variant={filter === f ? 'default' : 'outline'}
                            onClick={() => setFilter(f)}
                            size="sm"
                            className="capitalize whitespace-nowrap"
                        >
                            {f.replace('_', ' ')}
                        </Button>
                    ))}
                </div>
            </div>

            {/* List */}
            <div className="grid gap-4">
                {isLoading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => <div key={i} className="h-24 bg-secondary animate-pulse rounded-lg" />)}
                    </div>
                ) : filteredData?.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        No insights found matching your criteria.
                    </div>
                ) : (
                    filteredData?.map((item) => (
                        <Card key={item.id} className="hover:border-primary/50 transition-colors">
                            <CardContent className="p-4 md:p-6">
                                <div className="flex flex-col md:flex-row justify-between gap-4">
                                    <div className="flex-1 space-y-2">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className={cn("px-2 py-0.5 rounded-full text-xs font-medium border", getSentimentColor(item.sentiment))}>
                                                {item.sentiment}
                                            </span>
                                            {item.urgency && item.urgency !== 'low' && (
                                                <span className={cn("flex items-center gap-1 text-xs", getUrgencyColor(item.urgency))}>
                                                    <AlertCircle size={12} />
                                                    {item.urgency} Priority
                                                </span>
                                            )}
                                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                                                <Clock size={12} />
                                                {new Date(item.processed_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <p className="text-foreground/90 font-medium">{item.text_preview}</p>

                                        {/* Topics */}
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {item.topics?.map((topic, idx) => (
                                                <span key={idx} className="bg-secondary px-2 py-1 rounded text-xs text-secondary-foreground">
                                                    #{topic}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Action / Context */}
                                    <div className="flex md:flex-col items-center justify-center border-t md:border-t-0 md:border-l pt-4 md:pt-0 md:pl-4 gap-2">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">{Math.round((item.sentiment_score || 0) * 100)}%</div>
                                            <div className="text-xs text-muted-foreground">Confidence</div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
};

export default Insights;
