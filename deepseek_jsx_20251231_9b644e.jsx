import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, Loader } from 'lucide-react';
import { motion } from 'framer-motion';

const UploadArea = ({ onUpload, uploading = false, maxSize = 100 * 1024 * 1024 }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles);
    }
  }, [onUpload]);
  
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    maxSize,
    multiple: true,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/markdown': ['.md'],
      'text/html': ['.html', '.htm'],
    }
  });
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={uploading} />
        
        {uploading ? (
          <div className="space-y-3">
            <Loader className="w-12 h-12 mx-auto text-blue-500 animate-spin" />
            <p className="text-gray-600">Uploading documents...</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-blue-500" />
            </div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive ? 'Drop files here' : 'Upload documents'}
              </p>
              <p className="text-gray-500 mt-1">
                Drag & drop files or click to browse
              </p>
            </div>
            <div className="text-sm text-gray-400">
              Supports PDF, TXT, DOCX, MD, HTML
            </div>
            <div className="text-xs text-gray-400">
              Max file size: {formatFileSize(maxSize)}
            </div>
          </div>
        )}
      </div>
      
      {fileRejections.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <div className="flex items-center text-red-700">
            <X className="w-5 h-5 mr-2" />
            <span className="font-medium">Some files were rejected:</span>
          </div>
          <ul className="mt-2 text-sm text-red-600 list-disc list-inside">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.path}>
                {file.path} - {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </motion.div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
            <File className="w-5 h-5 text-blue-500" />
          </div>
          <h4 className="font-medium text-gray-800">PDF Documents</h4>
          <p className="text-sm text-gray-500 mt-1">Research papers, reports, books</p>
        </div>
        
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3">
            <File className="w-5 h-5 text-green-500" />
          </div>
          <h4 className="font-medium text-gray-800">Text Files</h4>
          <p className="text-sm text-gray-500 mt-1">Notes, code, plain text</p>
        </div>
        
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
            <File className="w-5 h-5 text-purple-500" />
          </div>
          <h4 className="font-medium text-gray-800">Office Docs</h4>
          <p className="text-sm text-gray-500 mt-1">Word documents, markdown</p>
        </div>
      </div>
    </div>
  );
};

export default UploadArea;