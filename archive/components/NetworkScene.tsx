import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, Group } from 'three'

function Node({ position, delay }: { position: [number, number, number], delay: number }) {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime() + delay
      meshRef.current.position.y = position[1] + Math.sin(time * 0.5) * 0.3
      meshRef.current.scale.setScalar(1 + Math.sin(time) * 0.1)
    }
  })

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshStandardMaterial color="#6366f1" emissive="#6366f1" emissiveIntensity={0.5} />
    </mesh>
  )
}

function Connection({ start, end }: { start: [number, number, number], end: [number, number, number] }) {
  const lineRef = useRef<any>(null)
  
  useFrame((state) => {
    if (lineRef.current) {
      const time = state.clock.getElapsedTime()
      lineRef.current.material.opacity = 0.3 + Math.sin(time * 2) * 0.2
    }
  })

  return (
    <line ref={lineRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={2}
          array={new Float32Array([...start, ...end])}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial color="#6366f1" transparent opacity={0.3} />
    </line>
  )
}

export function NetworkScene() {
  const groupRef = useRef<Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.1
    }
  })

  const nodes = [
    [0, 0, 0],
    [1.5, 0.5, 1],
    [-1.5, -0.5, 1],
    [1, 1, -1],
    [-1, -1, -1],
    [0, 1.5, 0],
    [0, -1.5, 0],
  ] as [number, number, number][]

  const connections = [
    [0, 1],
    [0, 2],
    [0, 3],
    [0, 4],
    [0, 5],
    [0, 6],
    [1, 3],
    [2, 4],
    [5, 3],
    [6, 4],
  ]

  return (
    <group ref={groupRef}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#6366f1" />
      
      {nodes.map((position, i) => (
        <Node key={i} position={position} delay={i * 0.5} />
      ))}
      
      {connections.map(([startIdx, endIdx]) => (
        <Connection
          key={`${startIdx}-${endIdx}`}
          start={nodes[startIdx]}
          end={nodes[endIdx]}
        />
      ))}
    </group>
  )
}
