import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  PieChart,
} from '@mui/icons-material';
import { financeAPI } from '../api/financeApi';
import type { FinancialSummary, Transaction } from '../api/financeApi';

interface StatCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="h2">
            {value}
          </Typography>
        </Box>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: '50%',
            p: 2,
            color: 'white',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [summaryData, transactionsData] = await Promise.all([
          financeAPI.getFinancialSummary(),
          financeAPI.getTransactions(),
        ]);
        
        setSummary(summaryData);
        // Get the 5 most recent transactions
        setRecentTransactions(transactionsData.slice(-5).reverse());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!summary) {
    return <Alert severity="warning">No financial data available</Alert>;
  }

  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Box display="flex" flexWrap="wrap" gap={2} sx={{ mb: 4 }}>
        <Box flex="1" minWidth="250px">
          <StatCard
            title="Total Income"
            value={formatCurrency(summary.total_income)}
            icon={<TrendingUp />}
            color="#4caf50"
          />
        </Box>
        <Box flex="1" minWidth="250px">
          <StatCard
            title="Total Expenses"
            value={formatCurrency(summary.total_expenses)}
            icon={<TrendingDown />}
            color="#f44336"
          />
        </Box>
        <Box flex="1" minWidth="250px">
          <StatCard
            title="Net Income"
            value={formatCurrency(summary.net_income)}
            icon={<AccountBalance />}
            color={summary.net_income >= 0 ? "#4caf50" : "#f44336"}
          />
        </Box>
        <Box flex="1" minWidth="250px">
          <StatCard
            title="Categories"
            value={Object.keys(summary.expense_by_category).length.toString()}
            icon={<PieChart />}
            color="#2196f3"
          />
        </Box>
      </Box>

      {/* Charts and Recent Transactions */}
      <Box display="flex" flexWrap="wrap" gap={2}>
        <Box flex="1" minWidth="400px">
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expenses by Category
              </Typography>
              {Object.entries(summary.expense_by_category).map(([category, amount]) => (
                <Box key={category} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">{category}</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {formatCurrency(amount)}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: '100%',
                      height: 8,
                      backgroundColor: '#e0e0e0',
                      borderRadius: 4,
                      mt: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: `${(amount / summary.total_expenses) * 100}%`,
                        height: '100%',
                        backgroundColor: '#2196f3',
                        borderRadius: 4,
                      }}
                    />
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Box>

        <Box flex="1" minWidth="400px">
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Transactions
              </Typography>
              {recentTransactions.length === 0 ? (
                <Typography color="textSecondary">No transactions found</Typography>
              ) : (
                recentTransactions.map((transaction, index) => (
                  <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #e0e0e0' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="body1" fontWeight="bold">
                          {transaction.description}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {transaction.category} • {transaction.date}
                        </Typography>
                      </Box>
                      <Typography
                        variant="body1"
                        fontWeight="bold"
                        color={transaction.amount >= 0 ? 'green' : 'red'}
                      >
                        {formatCurrency(transaction.amount)}
                      </Typography>
                    </Box>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
