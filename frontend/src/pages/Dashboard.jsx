import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import {
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  Smile,
  AlertTriangle,
  TrendingUp
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

const COLORS = ['#10b981', '#6b7280', '#ef4444']; // Positive (Green), Neutral (Gray), Negative (Red)

const DashboardSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-secondary rounded-lg" />)}
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="h-96 bg-secondary rounded-lg" />
      <div className="h-96 bg-secondary rounded-lg" />
    </div>
  </div>
)

const StatCard = ({ title, value, subtext, icon: Icon, trend }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex items-center justify-between space-y-0 pb-2">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {Icon && <Icon size={16} className="text-muted-foreground" />}
      </div>
      <div className="flex items-baseline gap-2 mt-2">
        <div className="text-2xl font-bold">{value}</div>
        {trend && (
          <span className={cn(
            "text-xs flex items-center",
            trend > 0 ? "text-green-500" : "text-red-500"
          )}>
            {trend > 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      {subtext && <p className="text-xs text-muted-foreground mt-1">{subtext}</p>}
    </CardContent>
  </Card>
)

const Dashboard = () => {
  // For now, grabbing the first entity again or all. 
  // Ideally, this state lives in a global context or URL param.
  // I'll fetch entities to get ID, then fetch dashboard.
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

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', effectiveId],
    queryFn: async () => {
      if (!effectiveId) return null;
      const res = await api.get(`/api/analysis/dashboard/?entity_id=${effectiveId}`);
      return res.data;
    },
    enabled: !!effectiveId,
  });

  if (isLoading && !data) return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading Analytics...</div>;
  if (error) return <div className="p-8 text-center text-destructive">Error loading dashboard: {error.message}</div>;

  // Fallback for empty state
  if (!data) return (
    <div className="flex flex-col items-center justify-center py-20 bg-secondary/10 rounded-xl border border-dashed">
      <h2 className="text-xl font-semibold mb-2">No Data Available</h2>
      <p className="text-muted-foreground mb-6">Create an entity and upload reviews in the Ingestion Hub to see analytics.</p>
      <div className="w-64">
        {entityList.length > 0 && (
          <select
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
            value={selectedEntity || ''}
            onChange={(e) => setSelectedEntity(e.target.value)}
          >
            {entityList.map(ent => (
              <option key={ent.id} value={ent.id}>{ent.name}</option>
            ))}
          </select>
        )}
      </div>
    </div>
  );

  // Process data for charts
  const sentimentData = [
    { name: 'Positive', value: data.sentiment_breakdown?.positive?.count || 0 },
    { name: 'Neutral', value: data.sentiment_breakdown?.neutral?.count || 0 },
    { name: 'Negative', value: data.sentiment_breakdown?.negative?.count || 0 },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-muted-foreground mt-1">AI-powered summary of your business performance.</p>
        </div>

        {/* Entity Selector */}
        <div className="flex items-center gap-3 bg-secondary/20 p-2 px-3 rounded-lg border border-border/50">
          <span className="text-sm font-medium">Business:</span>
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
      </div>{/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Feedback"
          value={data.total_feedbacks || 0}
          icon={MessageSquare}
          subtext="All time volume"
        />
        <StatCard
          title="Avg Sentiment"
          value={data.average_sentiment ? data.average_sentiment.toFixed(2) : "0.00"}
          icon={Smile}
          trend={0} // TODO: Calculate trend from previous period
        />
        <StatCard
          title="Critical Issues"
          value={data.critical_insights_count}
          icon={AlertTriangle}
          subtext="Action limit reached"
        />
        <StatCard
          title="Active Insights"
          value={data.active_insights_count}
          icon={TrendingUp}
          subtext="Opportunities detected"
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
        {/* Sentiment Trend Area Chart */}
        <Card className="lg:col-span-4 h-[400px]">
          <CardHeader>
            <CardTitle>Sentiment Trend (30 Days)</CardTitle>
          </CardHeader>
          <CardContent className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.sentiment_trend}>
                <defs>
                  <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={(str) => {
                    const d = new Date(str);
                    return `${d.getDate()}/${d.getMonth() + 1}`;
                  }}
                  stroke="#94a3b8"
                  fontSize={12}
                />
                <YAxis stroke="#94a3b8" fontSize={12} domain={[-1, 1]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area
                  type="monotone"
                  dataKey="average_sentiment"
                  stroke="#7c3aed"
                  fillOpacity={1}
                  fill="url(#colorSentiment)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Sentiment Distribution Pie */}
        <Card className="lg:col-span-3 h-[400px]">
          <CardHeader>
            <CardTitle>Sentiment Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="h-[320px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Legend Overlay */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
              <div className="text-3xl font-bold">{data.total_feedbacks}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row: Topics & Product Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Top Topics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(data.top_topics || []).map((item, idx) => (
                <div key={idx} className="flex items-center">
                  <div className="w-full">
                    <div className="flex justify-between text-sm mb-1">
                      <span>{item.topic}</span>
                      <span className="text-muted-foreground">{item.count}</span>
                    </div>
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(item.count / data.total_feedbacks) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Product Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(data.product_performance || []).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                  <div className="font-medium">{item.product}</div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex flex-col items-end">
                      <span className={cn(
                        item.avg_sentiment_score > 0 ? "text-green-500" : "text-red-500"
                      )}>
                        {item.avg_sentiment_score} Sent.
                      </span>
                      <span className="text-xs text-muted-foreground">{item.total_feedbacks} reviews</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
