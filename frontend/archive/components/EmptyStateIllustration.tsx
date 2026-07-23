import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, Group } from 'three'

function FloatingTorusKnot({ position, delay }: { position: [number, number, number], delay: number }) {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime() + delay
      meshRef.current.position.y = position[1] + Math.sin(time) * 0.15
      meshRef.current.rotation.x = time * 0.2
      meshRef.current.rotation.y = time * 0.3
    }
  })

  return (
    <mesh ref={meshRef} position={position}>
      <torusKnotGeometry args={[0.5, 0.15, 128, 32]} />
      <meshStandardMaterial 
        color="#818cf8" 
        roughness={0.2}
        metalness={0.8}
        emissive="#3730a3"
        emissiveIntensity={0.2}
      />
    </mesh>
  )
}

function FloatingIcosahedron({ position, delay, scale = 1, color = "#a78bfa" }: { position: [number, number, number], delay: number, scale?: number, color?: string }) {
  const groupRef = useRef<Group>(null)
  const meshRef = useRef<Mesh>(null)
  const wireframeRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime() + delay
      groupRef.current.position.y = position[1] + Math.cos(time) * 0.1
      groupRef.current.rotation.y = time * 0.2
      groupRef.current.rotation.z = time * 0.1
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.x = state.clock.getElapsedTime() * -0.1
      wireframeRef.current.rotation.y = state.clock.getElapsedTime() * -0.1
    }
  })

  return (
    <group ref={groupRef} position={position} scale={[scale, scale, scale]}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[0.4, 1]} />
        <meshStandardMaterial 
          color={color} 
          roughness={0.3}
          metalness={0.5}
        />
      </mesh>
      <mesh ref={wireframeRef}>
        <icosahedronGeometry args={[0.5, 1]} />
        <meshBasicMaterial color={color} wireframe transparent opacity={0.4} />
      </mesh>
    </group>
  )
}

function FloatingRings({ position, delay }: { position: [number, number, number], delay: number }) {
  const meshRef1 = useRef<Mesh>(null)
  const meshRef2 = useRef<Mesh>(null)
  
  useFrame((state) => {
    const time = state.clock.getElapsedTime() + delay
    if (meshRef1.current) {
      meshRef1.current.position.y = position[1] + Math.sin(time * 0.8) * 0.1
      meshRef1.current.rotation.x = time * 0.5
      meshRef1.current.rotation.y = time * 0.3
    }
    if (meshRef2.current) {
      meshRef2.current.position.y = position[1] + Math.sin(time * 0.8) * 0.1
      meshRef2.current.rotation.x = time * -0.4
      meshRef2.current.rotation.y = time * -0.2
    }
  })

  return (
    <group position={position}>
      <mesh ref={meshRef1}>
        <torusGeometry args={[0.6, 0.02, 16, 100]} />
        <meshStandardMaterial color="#38bdf8" emissive="#0ea5e9" emissiveIntensity={0.8} />
      </mesh>
      <mesh ref={meshRef2}>
        <torusGeometry args={[0.8, 0.02, 16, 100]} />
        <meshStandardMaterial color="#f472b6" emissive="#ec4899" emissiveIntensity={0.8} />
      </mesh>
    </group>
  )
}

export function EmptyStateIllustration() {
  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={1.5} color="#ffffff" />
      <pointLight position={[-10, -10, -10]} intensity={1} color="#6366f1" />
      <spotLight position={[0, 5, 0]} intensity={0.8} angle={Math.PI/4} penumbra={1} color="#8b5cf6" />
      
      {/* Centerpiece */}
      <FloatingTorusKnot position={[0, 0, 0]} delay={0} />
      
      {/* Surrounding floating objects */}
      <FloatingIcosahedron position={[-2, 0.5, -1]} delay={1.2} scale={0.8} />
      <FloatingIcosahedron position={[2, -0.5, 0.5]} delay={2.5} scale={1.2} color="#f43f5e" />
      <FloatingRings position={[1.5, 1, -1.5]} delay={0.5} />
      <FloatingRings position={[-1.5, -1, 1]} delay={1.8} />
    </>
  )
}
