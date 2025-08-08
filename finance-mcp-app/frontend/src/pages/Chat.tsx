import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { financeAPI } from '../api/financeApi';

interface ChatMessage {
  id: number;
  message: string;
  response: string;
  timestamp: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const messageId = Date.now();
    const userMessage = currentMessage;
    setCurrentMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await financeAPI.sendChatMessage(userMessage);
      
      setMessages(prev => [...prev, {
        id: messageId,
        message: userMessage,
        response: response,
        timestamp: new Date(),
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Finance Assistant
      </Typography>
      
      <Typography variant="body1" color="textSecondary" gutterBottom>
        Ask me anything about your finances! I can help you with transaction analysis, 
        budget planning, financial summaries, and more.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card sx={{ height: '60vh', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {/* Messages Area */}
          <Box 
            sx={{ 
              flex: 1, 
              overflowY: 'auto', 
              mb: 2,
              '&::-webkit-scrollbar': {
                width: '6px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#888',
                borderRadius: '3px',
              },
            }}
          >
            {messages.length === 0 ? (
              <Box 
                display="flex" 
                justifyContent="center" 
                alignItems="center" 
                height="100%" 
                color="text.secondary"
              >
                <Typography>
                  Start a conversation by asking about your finances!
                </Typography>
              </Box>
            ) : (
              <Box>
                {messages.map((msg) => (
                  <Box key={msg.id} sx={{ mb: 3 }}>
                    {/* User Message */}
                    <Box display="flex" justifyContent="flex-end" mb={1}>
                      <Paper
                        sx={{
                          p: 2,
                          backgroundColor: '#1976d2',
                          color: 'white',
                          maxWidth: '70%',
                          borderRadius: '18px 18px 4px 18px',
                        }}
                      >
                        <Typography variant="body1">{msg.message}</Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8, fontSize: '0.7rem' }}>
                          {msg.timestamp.toLocaleTimeString()}
                        </Typography>
                      </Paper>
                    </Box>
                    
                    {/* AI Response */}
                    <Box display="flex" justifyContent="flex-start">
                      <Paper
                        sx={{
                          p: 2,
                          backgroundColor: '#f5f5f5',
                          maxWidth: '70%',
                          borderRadius: '18px 18px 18px 4px',
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {msg.response}
                        </Typography>
                      </Paper>
                    </Box>
                  </Box>
                ))}
                
                {loading && (
                  <Box display="flex" justifyContent="flex-start" mb={2}>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: '#f5f5f5',
                        borderRadius: '18px 18px 18px 4px',
                      }}
                    >
                      <Box display="flex" alignItems="center" gap={1}>
                        <CircularProgress size={16} />
                        <Typography variant="body2" color="textSecondary">
                          AI is thinking...
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                )}
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box display="flex" gap={1} alignItems="flex-end">
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your finances..."
              disabled={loading}
              variant="outlined"
              size="small"
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={loading || !currentMessage.trim()}
              sx={{ minWidth: 'auto', p: 1.5 }}
            >
              <SendIcon />
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Example Questions */}
      <Box mt={2}>
        <Typography variant="h6" gutterBottom>
          Try asking:
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1}>
          {[
            "What's my current financial summary?",
            "Show me my recent transactions",
            "How much did I spend on food this month?",
            "What are my biggest expense categories?",
            "Add a transaction for $50 groceries",
          ].map((example, index) => (
            <Button
              key={index}
              variant="outlined"
              size="small"
              onClick={() => setCurrentMessage(example)}
              disabled={loading}
              sx={{ mb: 1 }}
            >
              {example}
            </Button>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default Chat;
