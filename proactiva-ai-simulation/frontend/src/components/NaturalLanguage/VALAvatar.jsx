import React from 'react';

const VALAvatar = ({ state, size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12', 
    large: 'w-16 h-16'
  };

  const textSizes = {
    small: 'text-sm',
    medium: 'text-lg',
    large: 'text-2xl'
  };

  // State-based animations and colors
  const getStateStyles = () => {
    switch (state) {
      case 'listening':
        return {
          avatar: 'animate-pulse ring-4 ring-red-200 bg-gradient-to-br from-red-500 to-pink-600',
          indicator: 'bg-red-500 animate-pulse',
          glow: 'shadow-lg shadow-red-200'
        };
      case 'thinking':
        return {
          avatar: 'animate-spin bg-gradient-to-br from-yellow-500 to-orange-600',
          indicator: 'bg-yellow-500',
          glow: 'shadow-lg shadow-yellow-200'
        };
      case 'speaking':
        return {
          avatar: 'animate-bounce bg-gradient-to-br from-green-500 to-emerald-600',
          indicator: 'bg-green-500 animate-pulse',
          glow: 'shadow-lg shadow-green-200'
        };
      case 'idle':
      default:
        return {
          avatar: 'bg-gradient-to-br from-blue-500 to-purple-600',
          indicator: 'bg-blue-500',
          glow: 'shadow-lg shadow-blue-200'
        };
    }
  };

  const styles = getStateStyles();

  return (
    <div className="relative">
      {/* Main VAL Avatar */}
      <div className={`
        ${sizeClasses[size]} 
        rounded-full 
        flex items-center justify-center 
        transition-all duration-300 
        ${styles.avatar} 
        ${styles.glow}
      `}>
        <span className={`text-white font-bold ${textSizes[size]}`}>V</span>
      </div>
      
      {/* Status Indicator */}
      <div className={`
        absolute -bottom-1 -right-1 
        w-4 h-4 rounded-full 
        border-2 border-white 
        transition-colors
        ${styles.indicator}
      `} />

      {/* Additional Visual Effects */}
      {state === 'listening' && (
        <div className="absolute inset-0 rounded-full">
          {/* Ripple effect for listening */}
          <div className="absolute inset-0 rounded-full bg-red-400 opacity-25 animate-ping" />
          <div className="absolute inset-0 rounded-full bg-red-400 opacity-25 animate-ping" style={{ animationDelay: '0.5s' }} />
        </div>
      )}

      {state === 'thinking' && (
        <div className="absolute -top-2 -right-2">
          {/* Thinking dots */}
          <div className="flex space-x-1">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="w-1.5 h-1.5 bg-yellow-500 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 200}ms` }}
              />
            ))}
          </div>
        </div>
      )}

      {state === 'speaking' && (
        <div className="absolute -top-1 -right-1">
          {/* Sound waves */}
          <div className="flex items-center space-x-0.5">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="w-0.5 bg-green-500 rounded-full animate-pulse"
                style={{
                  height: `${8 + (i * 2)}px`,
                  animationDelay: `${i * 100}ms`
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VALAvatar;