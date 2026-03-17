import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { portfolioApi, taskApi, wsUrlForTask } from '../api/client'
import type { TaskStatus } from '../api/client'

export default function Dashboard() {
  const { portfolioId: routePortfolioId } = useParams<{ portfolioId: string }>()
  const queryClient = useQueryClient()
  const [manualPortfolioId, setManualPortfolioId] = useState<string | undefined>(undefined)
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null)

  const portfoliosQuery = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioApi.list,
  })

  const selectedPortfolioId =
    routePortfolioId || manualPortfolioId || portfoliosQuery.data?.[0]?.id

  const portfolioQuery = useQuery({
    queryKey: ['portfolio', selectedPortfolioId],
    queryFn: () => portfolioApi.get(selectedPortfolioId!),
    enabled: Boolean(selectedPortfolioId),
  })

  const analysisQuery = useQuery({
    queryKey: ['analysis', selectedPortfolioId],
    queryFn: () => portfolioApi.getAnalysis(selectedPortfolioId!),
    enabled: Boolean(selectedPortfolioId),
    retry: false,
  })

  const runAnalysis = useMutation({
    mutationFn: async () => {
      if (!selectedPortfolioId) {
        throw new Error('portfolio_missing')
      }
      return portfolioApi.analyze(selectedPortfolioId)
    },
    onSuccess: async (result) => {
      const task = await taskApi.get(result.task_id)
      setTaskStatus(task)
    },
  })

  const currentTaskId = taskStatus?.task_id
  useEffect(() => {
    if (!currentTaskId) {
      return
    }

    const ws = new WebSocket(wsUrlForTask(currentTaskId))
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as TaskStatus
        setTaskStatus(payload)
        if (payload.status === 'completed') {
          queryClient.invalidateQueries({ queryKey: ['analysis', payload.portfolio_id] })
          queryClient.invalidateQueries({ queryKey: ['portfolio', payload.portfolio_id] })
        }
      } catch {
        // keep silent for malformed websocket payload
      }
    }

    return () => {
      ws.close()
    }
  }, [currentTaskId, queryClient])

  const allocationSummary = useMemo(() => {
    const positions = portfolioQuery.data?.positions || []
    return positions
      .map((p) => `${p.code}: ${(p.allocation * 100).toFixed(1)}%`)
      .join(' | ')
  }, [portfolioQuery.data?.positions])

  return (
    <div className="min-h-screen bg-stone-100 text-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-serif">Dashboard</h1>
            <p className="mt-1 text-sm text-stone-600">组合分析结果与任务进度</p>
          </div>
          <Link className="rounded border border-stone-300 bg-white px-4 py-2 text-sm" to="/">
            新建组合
          </Link>
        </header>

        <section className="mb-6 rounded-xl border border-stone-300 bg-white p-4">
          <label className="text-sm text-stone-600">选择组合</label>
          <select
            className="mt-2 w-full rounded border border-stone-300 px-3 py-2"
            value={selectedPortfolioId}
            onChange={(e) => setManualPortfolioId(e.target.value)}
          >
            {(portfoliosQuery.data || []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.id})
              </option>
            ))}
          </select>
        </section>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border border-stone-300 bg-white p-5">
            <h2 className="mb-3 text-xl font-serif">组合信息</h2>
            {!portfolioQuery.data ? (
              <p className="text-sm text-stone-500">暂无组合数据</p>
            ) : (
              <>
                <p className="text-sm">名称: {portfolioQuery.data.name}</p>
                <p className="text-sm">状态: {portfolioQuery.data.status}</p>
                <p className="text-sm">仓位: {allocationSummary}</p>
                <p className="text-sm">
                  偏好: {portfolioQuery.data.preferences.risk_level} / {portfolioQuery.data.preferences.horizon_months} months
                </p>
              </>
            )}

            <button
              onClick={() => runAnalysis.mutate()}
              disabled={!selectedPortfolioId || runAnalysis.isPending}
              className="mt-4 w-full rounded bg-stone-900 px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              {runAnalysis.isPending ? '提交任务中...' : 'Run Analysis'}
            </button>
          </section>

          <section className="rounded-xl border border-stone-300 bg-white p-5">
            <h2 className="mb-3 text-xl font-serif">任务进度</h2>
            {!taskStatus ? (
              <p className="text-sm text-stone-500">暂无任务</p>
            ) : (
              <>
                <p className="text-sm">Task: {taskStatus.task_id}</p>
                <p className="text-sm">Status: {taskStatus.status}</p>
                <p className="text-sm">Message: {taskStatus.message}</p>
                <p className="text-xs text-stone-500">
                  Updated: {new Date(taskStatus.timestamp).toLocaleString()}
                </p>
                <div className="mt-3 h-3 w-full overflow-hidden rounded bg-stone-200">
                  <div
                    className="h-3 bg-emerald-700 transition-all"
                    style={{ width: `${Math.max(0, Math.min(100, taskStatus.progress))}%` }}
                  />
                </div>
                <p className="mt-2 text-xs text-stone-500">{taskStatus.progress}%</p>
                {taskStatus.error && <p className="mt-1 text-sm text-red-700">Error: {taskStatus.error}</p>}
              </>
            )}
          </section>
        </div>

        <section className="mt-6 rounded-xl border border-stone-300 bg-white p-5">
          <h2 className="mb-3 text-xl font-serif">最新分析</h2>
          {analysisQuery.isLoading && <p className="text-sm text-stone-500">加载中...</p>}
          {analysisQuery.isError && <p className="text-sm text-stone-500">暂无分析结果</p>}
          {analysisQuery.data && (
            <>
              <p className="text-sm">评分: {analysisQuery.data.overall_score ?? '-'} / 100</p>
              <p className="mt-2 text-sm">{analysisQuery.data.summary}</p>

              <div className="mt-4">
                <h3 className="text-sm font-semibold">Recommendations</h3>
                <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
                  {analysisQuery.data.recommendations.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {analysisQuery.data.correlation_warnings.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-amber-700">Correlation Warnings</h3>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-amber-700">
                    {analysisQuery.data.correlation_warnings.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  )
}
