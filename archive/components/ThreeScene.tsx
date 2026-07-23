import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { ANIMATION_DURATION } from '@lib/constants'

interface Velocity {
  x: number
  y: number
  z: number
}

export function ThreeScene() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState(false)

  useEffect(() => {
    let mounted = true
    let animationFrameId: number

    const loadThree = async () => {
      try {
        const THREE = await import('three')
        
        if (!mounted || !containerRef.current) return

        const container = containerRef.current
        const scene = new THREE.Scene()
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000)
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
        
        renderer.setSize(container.clientWidth, container.clientHeight)
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        container.appendChild(renderer.domElement)

        // Create particles (reduced count for better performance on integrated GPUs)
        const particleCount = 40
        const particles = new THREE.BufferGeometry()
        const positions = new Float32Array(particleCount * 3)
        const velocities: Velocity[] = []

        for (let i = 0; i < particleCount; i++) {
          positions[i * 3] = (Math.random() - 0.5) * 10
          positions[i * 3 + 1] = (Math.random() - 0.5) * 10
          positions[i * 3 + 2] = (Math.random() - 0.5) * 10
          velocities.push({
            x: (Math.random() - 0.5) * 0.01,
            y: (Math.random() - 0.5) * 0.01,
            z: (Math.random() - 0.5) * 0.01
          })
        }

        particles.setAttribute('position', new THREE.BufferAttribute(positions, 3))

        const particleMaterial = new THREE.PointsMaterial({
          color: 0x6366f1,
          size: 0.05,
          transparent: true,
          opacity: 0.6
        })

        const particleSystem = new THREE.Points(particles, particleMaterial)
        scene.add(particleSystem)

        // Create connections (pre-allocate buffer to avoid allocations in loop)
        const lineMaterial = new THREE.LineBasicMaterial({
          color: 0x6366f1,
          transparent: true,
          opacity: 0.2
        })

        const maxConnections = particleCount * (particleCount - 1) / 2
        const linePositions = new Float32Array(maxConnections * 6)
        const linesGeometry = new THREE.BufferGeometry()
        linesGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3))
        const lines = new THREE.LineSegments(linesGeometry, lineMaterial)
        scene.add(lines)

        camera.position.z = 5

        // Mouse interaction
        let mouseX = 0
        let mouseY = 0

        const handleMouseMove = (event: MouseEvent) => {
          mouseX = (event.clientX / window.innerWidth) * 2 - 1
          mouseY = -(event.clientY / window.innerHeight) * 2 + 1
        }

        window.addEventListener('mousemove', handleMouseMove)

        // Animation
        const animate = () => {
          if (!mounted) return

          animationFrameId = requestAnimationFrame(animate)

          // Update particles
          const positions = particleSystem.geometry.attributes.position.array as Float32Array
          
          for (let i = 0; i < particleCount; i++) {
            positions[i * 3] += velocities[i].x
            positions[i * 3 + 1] += velocities[i].y
            positions[i * 3 + 2] += velocities[i].z

            // Boundary check
            if (Math.abs(positions[i * 3]) > 5) velocities[i].x *= -1
            if (Math.abs(positions[i * 3 + 1]) > 5) velocities[i].y *= -1
            if (Math.abs(positions[i * 3 + 2]) > 5) velocities[i].z *= -1
          }

          particleSystem.geometry.attributes.position.needsUpdate = true

          // Update connections (reuse pre-allocated buffer)
          let connectionIndex = 0
          for (let i = 0; i < particleCount; i++) {
            for (let j = i + 1; j < particleCount; j++) {
              const dx = positions[i * 3] - positions[j * 3]
              const dy = positions[i * 3 + 1] - positions[j * 3 + 1]
              const dz = positions[i * 3 + 2] - positions[j * 3 + 2]
              const distance = Math.sqrt(dx * dx + dy * dy + dz * dz)

              if (distance < 2) {
                linePositions[connectionIndex * 6] = positions[i * 3]
                linePositions[connectionIndex * 6 + 1] = positions[i * 3 + 1]
                linePositions[connectionIndex * 6 + 2] = positions[i * 3 + 2]
                linePositions[connectionIndex * 6 + 3] = positions[j * 3]
                linePositions[connectionIndex * 6 + 4] = positions[j * 3 + 1]
                linePositions[connectionIndex * 6 + 5] = positions[j * 3 + 2]
                connectionIndex++
              }
            }
          }

          // Update geometry with only the used portion
          lines.geometry.setDrawRange(0, connectionIndex * 2)
          lines.geometry.attributes.position.needsUpdate = true

          // Rotate based on mouse
          particleSystem.rotation.x += mouseY * 0.001
          particleSystem.rotation.y += mouseX * 0.001
          lines.rotation.x += mouseY * 0.001
          lines.rotation.y += mouseX * 0.001

          renderer.render(scene, camera)
        }

        animate()
        setIsLoaded(true)

        // Cleanup
        return () => {
          mounted = false
          window.removeEventListener('mousemove', handleMouseMove)
          cancelAnimationFrame(animationFrameId)
          if (container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement)
          }
          renderer.dispose()
          particleMaterial.dispose()
          lineMaterial.dispose()
          particles.dispose()
          linesGeometry.dispose()
        }
      } catch (err) {
        if (mounted) {
          setError(true)
        }
      }
    }

    loadThree()

    return () => {
      mounted = false
    }
  }, [])

  if (error) {
    return null // Graceful fallback - just don't render the 3D scene
  }

  return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isLoaded ? 1 : 0 }}
        transition={{ duration: ANIMATION_DURATION.NORMAL / 1000 }}
        ref={containerRef}
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 0 }}
        aria-hidden="true"
      />
  )
}
