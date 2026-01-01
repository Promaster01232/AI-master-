import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, model }, { rejectWithValue }) => {
    try {
      const response = await api.chat.completions({
        messages: [message],
        model,
      });
      return {
        userMessage: message,
        aiMessage: {
          ...response.choices[0].message,
          id: Date.now(),
          timestamp: new Date().toISOString(),
          model,
        },
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const loadChatHistory = createAsyncThunk(
  'chat/loadHistory',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.chat.history();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const clearChatHistory = createAsyncThunk(
  'chat/clearHistory',
  async (_, { rejectWithValue }) => {
    try {
      await api.chat.clearHistory();
      return [];
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    history: [],
    isLoading: false,
    error: null,
    currentConversationId: null,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    clearChat: (state) => {
      state.messages = [];
      state.currentConversationId = null;
    },
    setConversation: (state, action) => {
      state.messages = action.payload.messages || [];
      state.currentConversationId = action.payload.id;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push(action.payload.userMessage);
        state.messages.push(action.payload.aiMessage);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(loadChatHistory.fulfilled, (state, action) => {
        state.history = action.payload;
      })
      .addCase(clearChatHistory.fulfilled, (state) => {
        state.history = [];
        state.messages = [];
      });
  },
});

export const { addMessage, clearChat, setConversation } = chatSlice.actions;
export default chatSlice.reducer;