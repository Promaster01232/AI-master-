import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  messages: [],
  loading: false,
  error: null,
  selectedModel: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    setSelectedModel: (state, action) => {
      state.selectedModel = action.payload;
    },
    setMessages: (state, action) => {
      state.messages = action.payload;
    },
  },
});

export const {
  addMessage,
  setLoading,
  setError,
  clearMessages,
  setSelectedModel,
  setMessages,
} = chatSlice.actions;

export default chatSlice.reducer;
