import { Canvas } from '@react-three/fiber'
import { Suspense, useMemo } from 'react'
import { Loading } from '@components/common/Loading'
import { ErrorBoundary } from '@components/common/ErrorBoundary'

interface ThreeCanvasProps {
  children: React.ReactNode
  className?: string
  shadows?: boolean
  dpr?: [number, number]
}

export const ThreeCanvas = ({ children, className, shadows = false, dpr = [1, 2] }: ThreeCanvasProps) => {
  // Memoize canvas configuration to prevent unnecessary re-renders
  const canvasConfig = useMemo(
    () => ({
      gl: {
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance' as const,
      },
      dpr,
      shadows,
      camera: {
        position: [0, 0, 5],
        fov: 45,
        near: 0.1,
        far: 100,
      },
    }),
    [dpr, shadows]
  )

  const fallback = (
    <div className="flex items-center justify-center h-full w-full bg-slate-900/10 rounded-lg border border-slate-800/50">
      <p className="text-slate-500 text-sm p-4 text-center">
        3D rendering is not supported in your browser or environment.
      </p>
    </div>
  )

  return (
    <div className={className}>
      <ErrorBoundary fallback={fallback}>
        <Canvas 
          {...canvasConfig} 
          fallback={fallback}
        >
          <Suspense fallback={<Loading />}>{children}</Suspense>
        </Canvas>
      </ErrorBoundary>
    </div>
  )
}
