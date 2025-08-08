// API service for communicating with the Flask backend

export interface Transaction {
  id?: number;
  amount: number;
  description: string;
  category: string;
  date: string;
}

export interface FinancialSummary {
  total_income: number;
  total_expenses: number;
  net_income: number;
  expense_by_category: Record<string, number>;
}

export interface Budget {
  category: string;
  budgeted: number;
  spent: number;
  remaining: number;
}

export interface ChatMessage {
  message: string;
  response?: string;
}

class FinanceAPI {
  private baseURL = 'http://localhost:5003';

  async getTransactions(): Promise<Transaction[]> {
    const response = await fetch(`${this.baseURL}/api/transactions`);
    if (!response.ok) {
      throw new Error('Failed to fetch transactions');
    }
    return response.json();
  }

  async addTransaction(transaction: Omit<Transaction, 'id'>): Promise<Transaction> {
    const response = await fetch(`${this.baseURL}/api/add_transaction`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transaction),
    });
    if (!response.ok) {
      throw new Error('Failed to add transaction');
    }
    return response.json();
  }

  async getFinancialSummary(): Promise<FinancialSummary> {
    const response = await fetch(`${this.baseURL}/api/financial_summary`);
    if (!response.ok) {
      throw new Error('Failed to fetch financial summary');
    }
    return response.json();
  }

  async getBudgets(): Promise<Budget[]> {
    const response = await fetch(`${this.baseURL}/api/budgets`);
    if (!response.ok) {
      throw new Error('Failed to fetch budgets');
    }
    return response.json();
  }

  async sendChatMessage(message: string): Promise<string> {
    const response = await fetch(`${this.baseURL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) {
      throw new Error('Failed to send chat message');
    }
    const data = await response.json();
    return data.response;
  }

  async getCategories(): Promise<string[]> {
    const response = await fetch(`${this.baseURL}/api/categories`);
    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }
    return response.json();
  }
}

export const financeAPI = new FinanceAPI();
