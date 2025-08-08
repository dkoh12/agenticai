import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import { financeAPI } from '../api/financeApi';
import type { Budget } from '../api/financeApi';

const Budgets: React.FC = () => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBudgets = async () => {
      try {
        setLoading(true);
        const data = await financeAPI.getBudgets();
        setBudgets(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch budgets');
      } finally {
        setLoading(false);
      }
    };

    fetchBudgets();
  }, []);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const getProgressColor = (spent: number, budgeted: number) => {
    const percentage = (spent / budgeted) * 100;
    if (percentage >= 100) return 'error';
    if (percentage >= 80) return 'warning';
    return 'primary';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Budget Overview
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {budgets.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="textSecondary" align="center">
              No budget data available. Budget tracking is coming soon!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box display="flex" flexDirection="column" gap={2}>
          {budgets.map((budget, index) => {
            const percentage = (budget.spent / budget.budgeted) * 100;
            
            return (
              <Card key={index}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">{budget.category}</Typography>
                    <Typography
                      variant="body2"
                      color={budget.remaining >= 0 ? 'green' : 'red'}
                      fontWeight="bold"
                    >
                      {budget.remaining >= 0 ? 'Under budget' : 'Over budget'}
                    </Typography>
                  </Box>
                  
                  <Box mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="textSecondary">
                        Spent: {formatCurrency(budget.spent)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Budget: {formatCurrency(budget.budgeted)}
                      </Typography>
                    </Box>
                    
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(percentage, 100)}
                      color={getProgressColor(budget.spent, budget.budgeted)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    
                    <Box display="flex" justifyContent="space-between" mt={1}>
                      <Typography variant="body2" color="textSecondary">
                        {percentage.toFixed(1)}% used
                      </Typography>
                      <Typography
                        variant="body2"
                        color={budget.remaining >= 0 ? 'green' : 'red'}
                        fontWeight="bold"
                      >
                        {budget.remaining >= 0 ? 'Remaining: ' : 'Over by: '}
                        {formatCurrency(Math.abs(budget.remaining))}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            );
          })}
        </Box>
      )}
    </Box>
  );
};

export default Budgets;
