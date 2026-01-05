import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ProgressBar } from '../components/ui/ProgressBar';
import { UploadCloud, FileSpreadsheet, AlertCircle, CheckCircle, Clock, Trash2 } from 'lucide-react';
// import { useDropzone } from 'react-dropzone'; 
import { cn, formatDate } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const Upload = () => {
    const queryClient = useQueryClient();
    const [selectedEntity, setSelectedEntity] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploadError, setUploadError] = useState(null);

    // Entity Creation State
    const [isCreatingEntity, setIsCreatingEntity] = useState(false);
    const [newEntityName, setNewEntityName] = useState('');

    // 1. Fetch Entities
    const { data: entities, isLoading: entitiesLoading } = useQuery({
        queryKey: ['entities'],
        queryFn: async () => {
            const res = await api.get('/api/data-ingestion/entities/');
            return res.data;
        },
        onSuccess: (data) => {
            // Check if paginated or array
            const list = Array.isArray(data) ? data : data.results || [];
            if (list.length > 0 && !selectedEntity) {
                setSelectedEntity(list[0].id);
            } else if (list.length === 0) {
                // optionally trigger creation ?
            }
        }
    });

    // Helper to get safe list
    const entityList = React.useMemo(() => {
        if (!entities) return [];
        return Array.isArray(entities) ? entities : entities.results || [];
    }, [entities]);

    // Create Entity Mutation
    const createEntityMutation = useMutation({
        mutationFn: async (name) => {
            return api.post('/api/data-ingestion/entities/', { name });
        },
        onSuccess: (res) => {
            queryClient.invalidateQueries(['entities']);
            setIsCreatingEntity(false);
            setNewEntityName('');
            setSelectedEntity(res.data.id); // Auto-select new entity
        },
        onError: (err) => {
            console.error(err);
            const msg = err.response?.data ? JSON.stringify(err.response.data) : (err.message || "Unknown error");
            alert("Failed to create entity: " + msg);
        }
    });

    // Clear error when entity selection changes
    React.useEffect(() => {
        if (selectedEntity) setUploadError(null);
    }, [selectedEntity]);

    const handleCreateEntity = async (e) => {
        e.preventDefault();
        if (!newEntityName.trim()) return;
        createEntityMutation.mutate(newEntityName);
    }

    // 2. Fetch Batches (Polling)
    const { data: batches } = useQuery({
        queryKey: ['batches', selectedEntity],
        queryFn: async () => {
            if (!selectedEntity) return [];
            const res = await api.get(`/api/data-ingestion/batches/?entity=${selectedEntity}`);
            // DRF returns paginated { results: [] } usually, or list. Adapting to both.
            return Array.isArray(res.data) ? res.data : res.data.results || [];
        },
        enabled: !!selectedEntity,
        refetchInterval: 2000, // Poll every 2s for progress
    });

    // 3. Upload Mutation
    const uploadMutation = useMutation({
        mutationFn: async (file) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('entity_id', selectedEntity);
            formData.append('source', 'csv'); // Default

            return api.post('/api/data-ingestion/bulk-upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['batches']);
            setUploadError(null);
        },
        onError: (err) => {
            const msg = err.response?.data?.error || "Upload failed";
            setUploadError(msg);
        }
    });

    // 4. Delete Batch Mutation
    const deleteBatchMutation = useMutation({
        mutationFn: async (batchId) => {
            return api.delete(`/api/data-ingestion/batches/${batchId}/`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['batches']);
            queryClient.invalidateQueries(['dashboard']); // Refresh dashboard too
        },
        onError: (err) => {
            const msg = err.response?.data?.error || "Delete failed";
            alert("Failed to delete batch: " + msg);
        }
    });

    const handleDeleteBatch = (batch) => {
        if (window.confirm(`Delete "${batch.file_name}"?\n\nThis will remove ${batch.total_rows} feedbacks and their analysis. This action cannot be undone.`)) {
            deleteBatchMutation.mutate(batch.id);
        }
    };

    // Drag & Drop Handlers
    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        if (!selectedEntity) {
            setUploadError("Please select a business entity first.");
            return;
        }
        uploadMutation.mutate(file);
    };

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Ingestion Hub</h1>
                    <p className="text-muted-foreground mt-1">Upload reviews to feed the AI engine.</p>
                </div>

                {/* Entity Selector or Creator */}
                <div className="w-full md:w-auto flex items-center gap-2">
                    <span className="text-sm font-medium hidden md:inline-block">Select Business:</span>
                    {entitiesLoading ? (
                        <div className="h-10 w-48 bg-secondary animate-pulse rounded-md" />
                    ) : isCreatingEntity ? (
                        <form onSubmit={handleCreateEntity} className="flex gap-2">
                            <input
                                className="flex h-10 w-48 rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 ring-primary"
                                placeholder="Entity Name..."
                                value={newEntityName}
                                onChange={(e) => setNewEntityName(e.target.value)}
                                autoFocus
                            />
                            <Button size="sm" type="submit" disabled={createEntityMutation.isPending}>Save</Button>
                            <Button size="sm" variant="ghost" type="button" onClick={() => setIsCreatingEntity(false)}>Cancel</Button>
                        </form>
                    ) : (
                        <div className="flex gap-2">
                            {(entityList.length > 0) ? (
                                <select
                                    className="flex h-10 w-48 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                    value={selectedEntity || ''}
                                    onChange={(e) => setSelectedEntity(e.target.value)}
                                >
                                    {entityList.map(ent => (
                                        <option key={ent.id} value={ent.id}>{ent.name}</option>
                                    ))}
                                </select>
                            ) : (
                                <span className="text-sm text-yellow-500 flex items-center px-2">No entities found</span>
                            )}
                            <Button size="sm" variant="outline" onClick={() => setIsCreatingEntity(true)}>
                                + New
                            </Button>
                        </div>
                    )}
                </div>
            </div>

            {/* Upload Area */}
            <Card className={cn(
                "border-2 border-dashed transition-colors duration-200",
                dragActive ? "border-primary bg-primary/5" : "border-border",
                uploadMutation.isPending && "opacity-50 pointer-events-none"
            )}>
                <CardContent
                    className="flex flex-col items-center justify-center py-16 text-center cursor-pointer"
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        className="hidden"
                        id="file-upload"
                        accept=".csv,.xlsx,.xls,.json"
                        onChange={handleChange}
                    />

                    <div className="h-20 w-20 bg-primary/10 rounded-full flex items-center justify-center mb-6">
                        <UploadCloud className="h-10 w-10 text-primary" />
                    </div>

                    <h3 className="text-xl font-semibold mb-2">
                        {uploadMutation.isPending ? "Uploading..." : "Drag & drop your file here"}
                    </h3>
                    <p className="text-muted-foreground mb-6 max-w-sm">
                        Supports CSV, Excel, JSON. Max 10MB.
                        Required columns: <code className="bg-muted px-1 py-0.5 rounded text-xs">text</code> (or review/comment).
                    </p>

                    <label htmlFor="file-upload" className="cursor-pointer inline-block">
                        <div className={cn(
                            "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                            "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
                            "h-10 px-4 py-2"
                        )}>
                            {uploadMutation.isPending ? "Uploading..." : "Browse Files"}
                        </div>
                    </label>

                    {uploadError && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-6 p-3 bg-destructive/10 text-destructive rounded-md text-sm flex items-center gap-2"
                        >
                            <AlertCircle size={16} />
                            {uploadError}
                        </motion.div>
                    )}
                </CardContent>
            </Card>

            {/* Recent Batches */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Recent Uploads</h2>

                <div className="grid gap-4">
                    <AnimatePresence>
                        {batches?.map((batch) => (
                            <motion.div
                                key={batch.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                <Card className="group hover:border-primary/30 transition-all">
                                    <div className="p-4 flex flex-col md:flex-row items-center gap-4">
                                        <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                                            <FileSpreadsheet className="text-muted-foreground" />
                                        </div>

                                        <div className="flex-1 min-w-0 grid gap-1">
                                            <div className="flex items-center justify-between">
                                                <p className="font-medium truncate">{batch.file_name}</p>
                                                <span className={cn(
                                                    "text-xs px-2 py-0.5 rounded-full capitalize border",
                                                    batch.status === 'completed' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                                                        batch.status === 'processing' ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                                                            batch.status === 'failed' ? "bg-red-500/10 text-red-500 border-red-500/20" :
                                                                "bg-secondary text-muted-foreground border-transparent"
                                                )}>
                                                    {batch.status}
                                                </span>
                                            </div>
                                            <div className="flex text-xs text-muted-foreground gap-4">
                                                <span className="flex items-center gap-1"><Clock size={12} /> {formatDate(batch.created_at)}</span>
                                                <span>{batch.total_rows} rows</span>
                                            </div>
                                        </div>

                                        <div className="w-full md:w-1/3 flex items-center gap-2">
                                            <div className="flex-1">
                                                {batch.status !== 'completed' && batch.status !== 'failed' ? (
                                                    <ProgressBar
                                                        value={batch.processed_percentage}
                                                        label="AI Processing"
                                                        indicatorClassName="bg-blue-500"
                                                    />
                                                ) : batch.status === 'completed' ? (
                                                    <div className="flex items-center text-sm text-green-500 gap-2 justify-end">
                                                        <CheckCircle size={16} />
                                                        <span>Analysis Complete</span>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center text-sm text-red-500 gap-2 justify-end">
                                                        <AlertCircle size={16} />
                                                        <span>Failed</span>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Delete Button */}
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDeleteBatch(batch)}
                                                disabled={deleteBatchMutation.isPending}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive hover:bg-destructive/10"
                                            >
                                                <Trash2 size={16} />
                                            </Button>
                                        </div>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {(!batches || batches.length === 0) && (
                        <div className="text-center py-12 text-muted-foreground bg-accent/20 rounded-lg border border-dashed border-border">
                            No uploads found. Start by dropping a file above.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Upload;
