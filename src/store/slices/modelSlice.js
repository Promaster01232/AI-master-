import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  models: [],
  loading: false,
  error: null,
  currentModel: null,
  modelStatus: {},
};

const modelSlice = createSlice({
  name: 'models',
  initialState,
  reducers: {
    setModels: (state, action) => {
      state.models = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setCurrentModel: (state, action) => {
      state.currentModel = action.payload;
    },
    setModelStatus: (state, action) => {
      state.modelStatus = action.payload;
    },
    addModel: (state, action) => {
      state.models.push(action.payload);
    },
  },
});

export const {
  setModels,
  setLoading,
  setError,
  setCurrentModel,
  setModelStatus,
  addModel,
} = modelSlice.actions;

export default modelSlice.reducer;
