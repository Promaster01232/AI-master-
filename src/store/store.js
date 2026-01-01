import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './slices/chatSlice';
import modelReducer from './slices/modelSlice';
import documentReducer from './slices/documentSlice';
import userReducer from './slices/userSlice';

const store = configureStore({
  reducer: {
    chat: chatReducer,
    models: modelReducer,
    documents: documentReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export { store };
export default store;
