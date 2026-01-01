import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, Check, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ChatWindow = ({ messages, isLoading, onMessageAction }) => {
  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    // Show toast or feedback
  };
  
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-800 rounded-bl-none'
              }`}
            >
              <div className="flex items-center mb-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                  message.role === 'user' ? 'bg-blue-600' : 'bg-gray-200'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-5 h-5" />
                  ) : (
                    <Bot className="w-5 h-5" />
                  )}
                </div>
                <span className="text-sm font-medium">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </span>
                {message.timestamp && (
                  <span className="text-xs ml-2 opacity-75">
                    {new Date(message.timestamp).toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                )}
              </div>
              
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <div className="relative">
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                          <button
                            onClick={() => handleCopy(String(children))}
                            className="absolute top-2 right-2 p-1 bg-gray-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
              
              {message.role === 'assistant' && (
                <div className="flex items-center justify-between mt-3 pt-2 border-t border-opacity-20">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => onMessageAction?.(message, 'copy')}
                      className="p-1 hover:bg-white hover:bg-opacity-10 rounded"
                      title="Copy"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onMessageAction?.(message, 'like')}
                      className="p-1 hover:bg-white hover:bg-opacity-10 rounded"
                      title="Like"
                    >
                      <ThumbsUp className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onMessageAction?.(message, 'dislike')}
                      className="p-1 hover:bg-white hover:bg-opacity-10 rounded"
                      title="Dislike"
                    >
                      <ThumbsDown className="w-4 h-4" />
                    </button>
                  </div>
                  {message.model && (
                    <span className="text-xs px-2 py-1 bg-opacity-20 rounded">
                      {message.model}
                    </span>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      
      {isLoading && (
        <div className="flex items-center space-x-3 text-gray-500">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <Bot className="w-5 h-5 text-blue-500 animate-pulse" />
          </div>
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-sm">Thinking...</span>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;