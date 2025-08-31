import React, { useState } from 'react';
import { Email, EmailSummary } from '../types/email';
import { ArrowLeft, Paperclip, User, Clock, Send, Bot, Copy, CheckCircle } from 'lucide-react';

interface EmailDetailsProps {
  email: Email;
  summary?: EmailSummary;
  onBack: () => void;
  onSummarize: () => void;
}

const EmailDetails: React.FC<EmailDetailsProps> = ({ email, summary, onBack, onSummarize }) => {
  const [replyText, setReplyText] = useState('');
  const [selectedTone, setSelectedTone] = useState<'professional' | 'friendly' | 'brief'>('professional');
  const [copied, setCopied] = useState(false);

  const formatTime = (date: Date) => {
    return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const generateReply = () => {
    let reply = '';
    switch (selectedTone) {
      case 'professional':
        reply = summary?.suggestedResponse || 'Thank you for your email. I will review this matter and respond accordingly.';
        break;
      case 'friendly':
        reply = 'Hi! Thanks for reaching out. I appreciate you taking the time to share this with me. Let me look into this and get back to you soon!';
        break;
      case 'brief':
        reply = 'Thanks for the email. I\'ll review and respond shortly.';
        break;
    }
    setReplyText(reply);
  };

  const copyToClipboard = async () => {
    if (replyText) {
      await navigator.clipboard.writeText(replyText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Inbox
          </button>
          {!summary && (
            <button
              onClick={onSummarize}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Bot className="w-4 h-4 mr-2" />
              Generate Summary
            </button>
          )}
        </div>
      </div>

      {/* Email Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          {/* Email Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{email.from}</p>
                  <p className="text-sm text-gray-600">to {email.to}</p>
                  <p className="text-xs text-gray-500 flex items-center mt-1">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatTime(email.timestamp)}
                  </p>
                </div>
              </div>
              {email.hasAttachment && (
                <div className="flex items-center text-gray-500">
                  <Paperclip className="w-4 h-4 mr-1" />
                  <span className="text-sm">Attachment</span>
                </div>
              )}
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-4">{email.subject}</h1>

            {/* Summary Card */}
            {summary && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6 border-l-4 border-blue-400">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-blue-900 flex items-center">
                    <Bot className="w-5 h-5 mr-2" />
                    AI Summary
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    summary.urgency >= 7 ? 'bg-red-100 text-red-800' :
                    summary.urgency >= 4 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    Urgency: {summary.urgency}/10
                  </span>
                </div>
                
                <p className="text-blue-800 mb-3">{summary.summary}</p>
                
                {summary.keyPoints.length > 0 && (
                  <div className="mb-3">
                    <h4 className="font-medium text-blue-900 mb-2">Key Points:</h4>
                    <ul className="space-y-1">
                      {summary.keyPoints.map((point, index) => (
                        <li key={index} className="flex items-start text-blue-700">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {summary.actionItems.length > 0 && (
                  <div>
                    <h4 className="font-medium text-blue-900 mb-2">Action Items:</h4>
                    <ul className="space-y-1">
                      {summary.actionItems.map((item, index) => (
                        <li key={index} className="flex items-start text-blue-700">
                          <CheckCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Email Body */}
          <div className="prose max-w-none mb-8">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {email.body}
            </div>
          </div>

          {/* Reply Section */}
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Reply</h3>
            
            {/* Tone Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Response Tone:</label>
              <div className="flex space-x-3">
                {(['professional', 'friendly', 'brief'] as const).map((tone) => (
                  <button
                    key={tone}
                    onClick={() => setSelectedTone(tone)}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      selectedTone === tone
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {tone.charAt(0).toUpperCase() + tone.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Reply Button */}
            <button
              onClick={generateReply}
              className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all mb-4"
            >
              <Bot className="w-4 h-4 mr-2" />
              Generate {selectedTone} Reply
            </button>

            {/* Reply Text Area */}
            <div className="space-y-3">
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Type your reply here or generate one using AI..."
                className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              
              {/* Action Buttons */}
              <div className="flex items-center space-x-3">
                <button
                  className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  disabled={!replyText.trim()}
                >
                  <Send className="w-4 h-4 mr-2" />
                  Send Reply
                </button>
                
                {replyText && (
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    {copied ? (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailDetails;