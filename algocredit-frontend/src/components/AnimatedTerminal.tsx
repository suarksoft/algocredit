/**
 * Animated Terminal Component
 * Professional typing effect for code examples
 */

'use client'

import { useState, useEffect } from 'react'
import { CodeBracketIcon } from '@heroicons/react/24/outline'

interface AnimatedTerminalProps {
  code: string
  title?: string
  language?: string
  autoStart?: boolean
  speed?: number
}

export function AnimatedTerminal({ 
  code, 
  title = "Live Security Analysis",
  language = "javascript",
  autoStart = true,
  speed = 50 
}: AnimatedTerminalProps) {
  const [displayedCode, setDisplayedCode] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (!autoStart) return

    const timer = setTimeout(() => {
      startTyping()
    }, 1000)

    return () => clearTimeout(timer)
  }, [autoStart])

  const startTyping = () => {
    setIsTyping(true)
    setCurrentIndex(0)
    setDisplayedCode('')
    
    const typeNextChar = () => {
      if (currentIndex < code.length) {
        setDisplayedCode(prev => prev + code[currentIndex])
        setCurrentIndex(prev => prev + 1)
        
        // Variable speed for more natural typing
        const nextSpeed = code[currentIndex] === '\n' ? speed * 3 : speed
        setTimeout(typeNextChar, nextSpeed)
      } else {
        setIsTyping(false)
      }
    }
    
    typeNextChar()
  }

  const resetAnimation = () => {
    setDisplayedCode('')
    setCurrentIndex(0)
    setIsTyping(false)
    setTimeout(startTyping, 500)
  }

  return (
    <div className="bg-slate-900/95 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50 shadow-2xl hover:shadow-green-500/20 transition-all duration-500">
      {/* Terminal Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/20 rounded-lg">
            <CodeBracketIcon className="h-4 w-4 text-green-400" />
          </div>
          <h4 className="text-white font-semibold">{title}</h4>
          {isTyping && (
            <div className="flex items-center gap-2">
              <span className="text-green-400 text-xs">Executing...</span>
              <div className="text-green-400 text-xs">
                {Math.round((currentIndex / code.length) * 100)}%
              </div>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <div className="h-3 w-3 rounded-full bg-red-400 hover:bg-red-300 cursor-pointer" onClick={resetAnimation}></div>
          <div className="h-3 w-3 rounded-full bg-yellow-400 hover:bg-yellow-300 cursor-pointer"></div>
          <div className="h-3 w-3 rounded-full bg-green-400 hover:bg-green-300 cursor-pointer" onClick={startTyping}></div>
        </div>
      </div>
      
      {/* Terminal Content */}
      <div className="relative">
        <div className="text-sm overflow-x-auto leading-relaxed min-h-[400px] font-mono bg-slate-950/50 rounded-lg p-4">
          {/* Header Comment */}
          <div className="text-gray-400 mb-2">
            <span className="text-green-500">//</span> AlgoCredit Web3 Security Firewall - Live API Demo
          </div>
          <div className="text-gray-400 mb-4">
            <span className="text-green-500">//</span> Real TestNet endpoints with actual API key
          </div>
          
          {/* Simple code display - sade typing animation */}
          <pre className="text-green-400 whitespace-pre-wrap leading-relaxed">
            {displayedCode}
          </pre>
          
          {isTyping && (
            <span className="text-green-400">|</span>
          )}
        </div>
        
        {!isTyping && displayedCode && (
          <div className="absolute bottom-0 right-0 p-2">
            <button 
              onClick={resetAnimation}
              className="text-xs text-blue-400 hover:text-blue-300 bg-slate-800/50 px-2 py-1 rounded"
            >
              ↻ Replay
            </button>
          </div>
        )}
      </div>
      
      {/* Simple Stats */}
      {!isTyping && displayedCode && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-green-400 font-bold">&lt; 50ms</div>
            <div className="text-gray-400 text-xs">Response</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-blue-400 font-bold">99.9%</div>
            <div className="text-gray-400 text-xs">Accuracy</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-purple-400 font-bold">15K+</div>
            <div className="text-gray-400 text-xs">Secured</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnimatedTerminal
