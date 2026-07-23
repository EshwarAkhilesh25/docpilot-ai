import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh } from 'three'

function OrbRing({ radius, speed, delay }: { radius: number, speed: number, delay: number }) {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime() + delay
      meshRef.current.rotation.x = time * speed
      meshRef.current.rotation.y = time * speed * 0.5
    }
  })

  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[radius, 0.02, 16, 100]} />
      <meshStandardMaterial color="#6366f1" emissive="#6366f1" emissiveIntensity={0.3} transparent opacity={0.6} />
    </mesh>
  )
}

function CoreOrb() {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime()
      meshRef.current.scale.setScalar(1 + Math.sin(time * 2) * 0.1)
      meshRef.current.rotation.y = time * 0.5
    }
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color="#8b5cf6" emissive="#8b5cf6" emissiveIntensity={0.5} />
    </mesh>
  )
}

export function AIOrbScene() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8b5cf6" />
      
      <CoreOrb />
      <OrbRing radius={0.7} speed={0.3} delay={0} />
      <OrbRing radius={0.9} speed={0.2} delay={1} />
      <OrbRing radius={1.1} speed={0.15} delay={2} />
    </>
  )
}
