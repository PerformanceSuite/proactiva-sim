import React, { useState, useRef, useEffect } from 'react';
import { 
  Mic, 
  MicOff, 
  Send, 
  Volume2, 
  VolumeX, 
  MessageSquare, 
  Brain,
  Loader2,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import VALAvatar from './VALAvatar';

const NaturalLanguageQuery = ({ simulationId, onQueryResult }) => {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    // Check for speech recognition support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      setIsVoiceEnabled(true);
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setError('');
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const speakResponse = (text) => {
    if (synthRef.current && text) {
      synthRef.current.cancel(); // Stop any ongoing speech
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      synthRef.current.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const processQuery = async () => {
    if (!query.trim() || !simulationId) return;

    setIsProcessing(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/api/v2/simulations/${simulationId}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          include_context: true,
          voice_response: true
        }),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Add to conversation history
      const newEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        query: query,
        response: data.response,
        metrics: data.metrics || {},
        insights: data.insights || []
      };
      
      setConversationHistory(prev => [newEntry, ...prev]);
      setResponse(data.response);
      
      // Trigger callback with results
      if (onQueryResult) {
        onQueryResult(data);
      }
      
      // Speak the response if voice is enabled
      if (isVoiceEnabled && data.response) {
        speakResponse(data.response);
      }
      
      setQuery('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      processQuery();
    }
  };

  const quickQueries = [
    "What's the current wait time?",
    "How many patients are in triage?",
    "Show me the busiest department",
    "What insights do you have?",
    "How effective is VR therapy?",
    "What's the average provider workload?"
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-4">
        <VALAvatar 
          size="medium"
          state={
            isListening ? 'listening' :
            isProcessing ? 'thinking' :
            isSpeaking ? 'speaking' :
            'idle'
          }
        />
        
        <div className="ml-3">
          <h3 className="text-lg font-semibold text-gray-900">VAL</h3>
          <p className="text-sm text-gray-500">
            {isListening ? 'Listening...' :
             isProcessing ? 'Thinking...' :
             isSpeaking ? 'Speaking...' :
             'Virtual Assistant'}
          </p>
        </div>
        
        {isVoiceEnabled && (
          <div className="ml-auto flex items-center space-x-2">
            <span className="text-sm text-gray-500">Voice Ready</span>
            <CheckCircle className="w-4 h-4 text-green-500" />
          </div>
        )}
      </div>

      {/* Query Input */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your simulation... (e.g., 'What's the current wait time?')"
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="2"
              disabled={isProcessing || isListening}
            />
            {isListening && (
              <div className="absolute inset-0 bg-red-50 rounded-lg flex items-center justify-center">
                <div className="flex items-center text-red-600">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
                  Listening...
                </div>
              </div>
            )}
          </div>
          
          {/* Voice Controls */}
          {isVoiceEnabled && (
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`p-3 rounded-lg transition-colors ${
                isListening 
                  ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                  : 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              }`}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          )}
          
          {/* Send Button */}
          <button
            onClick={processQuery}
            disabled={!query.trim() || isProcessing || isListening}
            className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send query"
          >
            {isProcessing ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Voice Visualization */}
      {(isListening || isProcessing || isSpeaking) && (
        <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
          <div className="flex items-center justify-center space-x-1">
            {/* Voice Waveform Animation */}
            {isListening && (
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-blue-500 rounded-full animate-pulse"
                    style={{
                      height: `${Math.random() * 20 + 10}px`,
                      animationDelay: `${i * 100}ms`,
                      animationDuration: '1s'
                    }}
                  />
                ))}
              </div>
            )}
            
            {/* Thinking Animation */}
            {isProcessing && (
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={i}
                      className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 200}ms` }}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-600">VAL is analyzing your question...</span>
              </div>
            )}
            
            {/* Speaking Animation */}
            {isSpeaking && (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-500 rounded-full animate-ping" />
                <span className="text-sm text-gray-600">VAL is responding...</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Query Buttons */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Ask VAL:</p>
        <div className="flex flex-wrap gap-2">
          {quickQueries.map((quickQuery, index) => (
            <button
              key={index}
              onClick={() => setQuery(quickQuery)}
              disabled={isProcessing || isListening}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              {quickQuery}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* VAL Response Display */}
      {response && (
        <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-xs">V</span>
              </div>
              <span className="text-sm font-medium text-blue-800">VAL's Analysis:</span>
            </div>
            {isVoiceEnabled && (
              <button
                onClick={isSpeaking ? stopSpeaking : () => speakResponse(response)}
                className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
                title={isSpeaking ? 'Stop VAL speaking' : 'Have VAL read aloud'}
              >
                {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            )}
          </div>
          <p className="text-gray-800">{response}</p>
        </div>
      )}

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700 flex items-center">
            <MessageSquare className="w-4 h-4 mr-1" />
            Conversation with VAL
          </h4>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {conversationHistory.slice(0, 5).map((entry) => (
              <div key={entry.id} className="p-3 bg-gray-50 rounded-lg text-sm">
                <div className="font-medium text-gray-900 mb-1">
                  Q: {entry.query}
                </div>
                <div className="text-gray-700 mb-1">
                  A: {entry.response}
                </div>
                <div className="text-xs text-gray-500">
                  {entry.timestamp}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voice Status Indicator */}
      {(isListening || isSpeaking) && (
        <div className="mt-4 p-2 bg-gray-100 rounded-lg text-center">
          <div className="flex items-center justify-center space-x-2">
            {isListening && (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-700">Listening for your question...</span>
              </>
            )}
            {isSpeaking && (
              <>
                <Volume2 className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-gray-700">Speaking response...</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NaturalLanguageQuery;