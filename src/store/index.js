/**
 * Redux Store Configuration
 * 
 * This module sets up the Redux store with the following slices:
 * - chat: Chat state including messages and model selection
 * - models: Available models and current model status
 * - documents: Document management and chunks
 * - user: User authentication and profile
 * 
 * Usage:
 *   import { store } from './store/store';
 *   import { useSelector, useDispatch } from 'react-redux';
 * 
 *   // In your component:
 *   const messages = useSelector(state => state.chat.messages);
 *   const dispatch = useDispatch();
 */

export { store as default } from './store';
export { store } from './store';
