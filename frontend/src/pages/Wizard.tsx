import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { portfolioApi } from '../api/client'
import type { RiskLevel } from '../api/client'

interface DraftPosition {
  code: string
  allocation: string
}

const initialPositions: DraftPosition[] = [
  { code: '', allocation: '0.50' },
  { code: '', allocation: '0.50' },
]

export default function Wizard() {
  const navigate = useNavigate()
  const [name, setName] = useState('我的基金组合')
  const [positions, setPositions] = useState<DraftPosition[]>(initialPositions)
  const [riskLevel, setRiskLevel] = useState<RiskLevel>('medium')
  const [horizonMonths, setHorizonMonths] = useState('12')

  const allocationSum = useMemo(
    () => positions.reduce((acc, p) => acc + (parseFloat(p.allocation) || 0), 0),
    [positions],
  )

  const createPortfolio = useMutation({
    mutationFn: () =>
      portfolioApi.create({
        name,
        positions: positions.map((p) => ({
          code: p.code.trim(),
          allocation: parseFloat(p.allocation),
        })),
        preferences: {
          risk_level: riskLevel,
          horizon_months: parseInt(horizonMonths, 10),
        },
      }),
    onSuccess: (portfolio) => {
      navigate(`/dashboard/${portfolio.id}`)
    },
  })

  const updatePosition = (index: number, patch: Partial<DraftPosition>) => {
    setPositions((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)))
  }

  const addPosition = () => {
    setPositions((prev) => [...prev, { code: '', allocation: '0.00' }])
  }

  const removePosition = (index: number) => {
    setPositions((prev) => prev.filter((_, i) => i !== index))
  }

  const canSubmit =
    name.trim().length > 0 &&
    positions.length > 0 &&
    positions.every((p) => p.code.trim() && Number.isFinite(parseFloat(p.allocation))) &&
    Math.abs(allocationSum - 1) < 0.001 &&
    parseInt(horizonMonths, 10) > 0

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!canSubmit) {
      return
    }
    createPortfolio.mutate()
  }

  return (
    <div className="min-h-screen bg-amber-50 text-stone-900">
      <div className="mx-auto max-w-4xl px-6 py-12">
        <header className="mb-8">
          <h1 className="text-4xl font-serif">Prism Wizard</h1>
          <p className="mt-2 text-sm text-stone-600">首次配置你的基金组合和风险偏好</p>
        </header>

        <form onSubmit={onSubmit} className="space-y-8 rounded-2xl border border-amber-200 bg-white p-6 shadow-sm">
          <section>
            <h2 className="mb-3 text-xl font-serif">1. 组合名称</h2>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded border border-stone-300 px-3 py-2 text-sm"
              placeholder="例如：稳健长期组合"
            />
          </section>

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xl font-serif">2. 持仓基金与仓位</h2>
              <button
                type="button"
                onClick={addPosition}
                className="rounded border border-stone-300 px-3 py-1 text-xs"
              >
                添加基金
              </button>
            </div>

            <div className="space-y-3">
              {positions.map((position, index) => (
                <div key={index} className="grid grid-cols-12 gap-3">
                  <input
                    className="col-span-7 rounded border border-stone-300 px-3 py-2 text-sm"
                    placeholder="基金代码，例如 000273"
                    value={position.code}
                    onChange={(e) => updatePosition(index, { code: e.target.value })}
                  />
                  <input
                    className="col-span-3 rounded border border-stone-300 px-3 py-2 text-sm"
                    placeholder="占比"
                    value={position.allocation}
                    onChange={(e) => updatePosition(index, { allocation: e.target.value })}
                  />
                  <button
                    type="button"
                    onClick={() => removePosition(index)}
                    className="col-span-2 rounded border border-red-200 px-2 py-2 text-xs text-red-700"
                    disabled={positions.length <= 1}
                  >
                    删除
                  </button>
                </div>
              ))}
            </div>

            <p className="mt-2 text-xs text-stone-600">仓位总和必须为 1.00，当前为 {allocationSum.toFixed(2)}</p>
          </section>

          <section>
            <h2 className="mb-3 text-xl font-serif">3. 风险收益偏好</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="text-sm">
                风险等级
                <select
                  className="mt-1 w-full rounded border border-stone-300 px-3 py-2"
                  value={riskLevel}
                  onChange={(e) => setRiskLevel(e.target.value as RiskLevel)}
                >
                  <option value="low">低风险</option>
                  <option value="medium">中风险</option>
                  <option value="high">高风险</option>
                </select>
              </label>

              <label className="text-sm">
                投资期限（月）
                <input
                  className="mt-1 w-full rounded border border-stone-300 px-3 py-2"
                  type="number"
                  min={1}
                  value={horizonMonths}
                  onChange={(e) => setHorizonMonths(e.target.value)}
                />
              </label>
            </div>
          </section>

          <button
            type="submit"
            disabled={!canSubmit || createPortfolio.isPending}
            className="w-full rounded bg-stone-900 px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
          >
            {createPortfolio.isPending ? '创建中...' : '创建组合并进入 Dashboard'}
          </button>

          {createPortfolio.isError && (
            <p className="text-sm text-red-700">创建失败，请检查输入后重试。</p>
          )}
        </form>
      </div>
    </div>
  )
}
