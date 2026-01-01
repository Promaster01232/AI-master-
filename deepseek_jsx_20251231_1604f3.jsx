import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Send, Bot, User, Settings, Download, Upload } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import ChatWindow from '../components/Chat/ChatWindow';
import MessageBubble from '../components/Chat/MessageBubble';
import InputBox from '../components/Chat/InputBox';
import ModelSelector from '../components/Sidebar/ModelSelector';
import HistoryPanel from '../components/Sidebar/HistoryPanel';
import { sendMessage, clearChat, loadChatHistory } from '../store/slices/chatSlice';
import { getModels } from '../store/slices/modelSlice';
import api from '../services/api';

const Chat = () => {
  const dispatch = useDispatch();
  const messagesEndRef = useRef(null);
  
  const { messages, isLoading, history } = useSelector((state) => state.chat);
  const { models, currentModel } = useSelector((state) => state.models);
  const [input, setInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  useEffect(() => {
    dispatch(getModels());
    dispatch(loadChatHistory());
  }, [dispatch]);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };
    
    dispatch(sendMessage({
      message: userMessage,
      model: currentModel,
    }));
    
    setInput('');
    
    try {
      const response = await api.chat.completions({
        messages: [...messages.map(m => ({ role: m.role, content: m.content })), userMessage],
        model: currentModel,
      });
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.choices[0].message.content,
        timestamp: new Date().toISOString(),
        model: currentModel,
      };
      
      dispatch(sendMessage({
        message: aiMessage,
        model: currentModel,
      }));
      
    } catch (error) {
      console.error('Chat error:', error);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  const handleClearChat = () => {
    if (window.confirm('Clear chat history?')) {
      dispatch(clearChat());
    }
  };
  
  const handleExportChat = () => {
    const chatData = {
      messages,
      timestamp: new Date().toISOString(),
      model: currentModel,
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="w-80 border-r border-gray-200 bg-white overflow-y-auto"
          >
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">AI Models</h2>
              <ModelSelector />
              
              <h2 className="text-lg font-semibold text-gray-800 mt-8 mb-4">Chat History</h2>
              <HistoryPanel />
              
              <div className="mt-6 space-y-2">
                <button
                  onClick={handleClearChat}
                  className="w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg flex items-center"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Clear Chat
                </button>
                <button
                  onClick={handleExportChat}
                  className="w-full px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg flex items-center"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Chat
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 bg-white p-4 flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg mr-2"
            >
              <Settings className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold text-gray-800">AI Chat</h1>
            {currentModel && (
              <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
                {currentModel}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`px-3 py-1 rounded-full text-sm ${
              isLoading 
                ? 'bg-amber-100 text-amber-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {isLoading ? 'Thinking...' : 'Ready'}
            </div>
          </div>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <Bot className="w-16 h-16 mb-4 text-gray-300" />
              <h3 className="text-xl font-medium mb-2">Start a conversation</h3>
              <p className="text-gray-500 mb-6">Ask me anything or try one of these examples:</p>
              <div className="grid grid-cols-2 gap-3 max-w-md">
                {[
                  'Explain quantum computing in simple terms',
                  'Write a Python function to sort a list',
                  'Tell me a joke about programming',
                  'What are the benefits of AI?'
                ].map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(example)}
                    className="p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-3xl mx-auto">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2 text-gray-500">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-blue-500" />
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
        
        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-4">
          <InputBox
            value={input}
            onChange={setInput}
            onSend={handleSend}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;