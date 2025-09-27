/**
 * Optimized Loading Components
 * 24-Hour Sprint Performance Enhancement
 */

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  color?: 'blue' | 'purple' | 'green' | 'gray'
  text?: string
}

export function LoadingSpinner({ 
  size = 'md', 
  color = 'blue', 
  text 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
  }

  const colorClasses = {
    blue: 'border-blue-600',
    purple: 'border-purple-600',
    green: 'border-green-600',
    gray: 'border-gray-600'
  }

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div 
        className={`animate-spin rounded-full border-2 border-gray-200 border-t-transparent ${sizeClasses[size]} ${colorClasses[color]}`}
      />
      {text && (
        <p className="mt-2 text-sm text-gray-600">{text}</p>
      )}
    </div>
  )
}

interface SkeletonProps {
  className?: string
  count?: number
}

export function Skeleton({ className = "h-4 bg-gray-200 rounded", count = 1 }: SkeletonProps) {
  return (
    <div className="animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`${className} ${i > 0 ? 'mt-2' : ''}`} />
      ))}
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="animate-pulse">
        <div className="flex items-center space-x-4">
          <div className="rounded-full bg-gray-200 h-10 w-10"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
        <div className="mt-4 space-y-2">
          <div className="h-3 bg-gray-200 rounded"></div>
          <div className="h-3 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    </div>
  )
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-8 sm:grid-cols-4">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-16 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-24 mx-auto"></div>
          </div>
        </div>
      ))}
    </div>
  )
}
