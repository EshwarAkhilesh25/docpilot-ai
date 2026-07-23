import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, Group } from 'three'

function DocumentCube({ position, delay }: { position: [number, number, number], delay: number }) {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime() + delay
      meshRef.current.position.y = position[1] + Math.sin(time * 0.5) * 0.2
      meshRef.current.rotation.x = time * 0.3
      meshRef.current.rotation.y = time * 0.2
    }
  })

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.4, 0.5, 0.05]} />
      <meshStandardMaterial color="#6366f1" metalness={0.3} roughness={0.4} />
    </mesh>
  )
}

export function DocumentCubesScene() {
  const groupRef = useRef<Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.1
    }
  })

  const cubes = [
    [0, 0, 0],
    [1, 0.3, 0.5],
    [-1, -0.3, 0.5],
    [0.5, 0.5, -0.5],
    [-0.5, -0.5, -0.5],
  ] as [number, number, number][]

  return (
    <group ref={groupRef}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#6366f1" />
      
      {cubes.map((position, i) => (
        <DocumentCube key={i} position={position} delay={i * 0.3} />
      ))}
    </group>
  )
}
