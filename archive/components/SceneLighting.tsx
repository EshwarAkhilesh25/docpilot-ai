

export const SceneLighting = () => {
  return (
    <>
      {/* Ambient light for base illumination */}
      <AmbientLight intensity={0.5} />

      {/* Main directional light */}
      <DirectionalLight
        position={[10, 10, 5]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      {/* Fill light */}
      <PointLight position={[-10, 0, -10]} intensity={0.5} color="#4f46e5" />

      {/* Rim light */}
      <PointLight position={[10, 0, -10]} intensity={0.3} color="#8b5cf6" />
    </>
  )
}
