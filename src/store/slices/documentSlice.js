import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  documents: [],
  loading: false,
  error: null,
  selectedDocument: null,
  chunks: [],
};

const documentSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setDocuments: (state, action) => {
      state.documents = action.payload;
    },
    addDocument: (state, action) => {
      state.documents.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setSelectedDocument: (state, action) => {
      state.selectedDocument = action.payload;
    },
    setChunks: (state, action) => {
      state.chunks = action.payload;
    },
    removeDocument: (state, action) => {
      state.documents = state.documents.filter(
        doc => doc.id !== action.payload
      );
    },
  },
});

export const {
  setDocuments,
  addDocument,
  setLoading,
  setError,
  setSelectedDocument,
  setChunks,
  removeDocument,
} = documentSlice.actions;

export default documentSlice.reducer;
