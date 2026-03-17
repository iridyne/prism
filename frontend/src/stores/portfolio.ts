import { create } from 'zustand';

interface Portfolio {
  id: string;
  name: string;
  description?: string;
  holdings: Holding[];
}

interface Holding {
  id: string;
  fund_code: string;
  shares: number;
  cost_basis: number;
  current_price?: number;
  current_value?: number;
  pnl?: number;
  return_pct?: number;
}

interface PortfolioStore {
  currentPortfolio: Portfolio | null;
  setCurrentPortfolio: (portfolio: Portfolio) => void;
  clearPortfolio: () => void;
}

export const usePortfolioStore = create<PortfolioStore>((set) => ({
  currentPortfolio: null,
  setCurrentPortfolio: (portfolio) => set({ currentPortfolio: portfolio }),
  clearPortfolio: () => set({ currentPortfolio: null }),
}));
