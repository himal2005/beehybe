import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Cube Splitter", layout="wide")

st.title("🎲 Interactive 3D Cube Splitter")
st.write("Click the cube directly to drop and split it. Click anywhere else in the scene to gather all active cubes to that point!")

# HTML, CSS, and JavaScript (Three.js + Cannon-es physics)
game_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background-color: #1a1a1a;
      font-family: sans-serif;
    }
    #canvas-container {
      width: 100vw;
      height: 600px;
    }
  </style>
  <!-- Three.js for 3D Graphics -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <!-- Cannon.js for 3D Physics -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"></script>
</head>
<body>
  <div id="canvas-container"></div>

  <script>
    const container = document.getElementById('canvas-container');

    // 1. THREE.JS SCENE SETUP
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x141419);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 600, 0.1, 1000);
    camera.position.set(0, 5, 18);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, 600);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    scene.add(dirLight);

    // 2. CANNON PHYSICS WORLD
    const world = new CANNON.World();
    world.gravity.set(0, -20, 0); // Punchy gravity

    const bouncyMaterial = new CANNON.Material('bouncy');
    const contactMaterial = new CANNON.ContactMaterial(bouncyMaterial, bouncyMaterial, {
      friction: 0.2,
      restitution: 0.8 // High bounce factor
    });
    world.addContactMaterial(contactMaterial);

    // Ground Plane Physics & Visuals
    const groundBody = new CANNON.Body({
      mass: 0,
      shape: new CANNON.Plane(),
      material: bouncyMaterial
    });
    groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    groundBody.position.set(0, -5, 0);
    world.addBody(groundBody);

    const groundMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(100, 100),
      new THREE.MeshStandardMaterial({ color: 0x22222e, roughness: 0.8 })
    );
    groundMesh.rotation.x = -Math.PI / 2;
    groundMesh.position.y = -5;
    groundMesh.receiveShadow = true;
    scene.add(groundMesh);

    // Active Cubes Array
    const cubes = [];

    // 3. CUBE CREATION FUNCTION
    function createCube(position, size, isInitial = false) {
      const color = new THREE.Color().setHSL(Math.random(), 0.85, 0.55);

      // Three.js Mesh
      const geometry = new THREE.BoxGeometry(size, size, size);
      const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.3 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Cannon.js Physics Body
      const shape = new CANNON.Box(new CANNON.Vec3(size / 2, size / 2, size / 2));
      const body = new CANNON.Body({
        mass: isInitial ? 0 : size * 2,
        shape: shape,
        material: bouncyMaterial
      });
      body.position.copy(position);
      world.addBody(body);

      const cubeObj = { mesh, body, size, isInitial };
      cubes.push(cubeObj);
      return cubeObj;
    }

    // Spawn central starting cube
    createCube(new CANNON.Vec3(0, 2, 0), 3, true);

    // 4. CUBE SPLITTING FUNCTION
    function splitCube(cubeIndex) {
      const parent = cubes[cubeIndex];

      // Remove parent from rendering and physics
      scene.remove(parent.mesh);
      world.remove(parent.body);
      cubes.splice(cubeIndex, 1);

      // Calculate smaller cube size
      const newSize = parent.size * 0.75;
      if (newSize < 0.25) return; // Prevent infinitely tiny cubes

      // Spawn two child cubes
      for (let i = 0; i < 2; i++) {
        const offset = (i === 0 ? -1 : 1) * (newSize / 2);
        const childPos = new CANNON.Vec3(
          parent.body.position.x + offset,
          parent.body.position.y + 0.2,
          parent.body.position.z
        );

        const child = createCube(childPos, newSize, false);

        // Impart explosive outward velocity when splitting
        child.body.velocity.set(
          (Math.random() - 0.5) * 6 + (i === 0 ? -3 : 3),
          Math.random() * 5 + 3,
          (Math.random() - 0.5) * 6
        );
      }
    }

    // 5. CLICK INTERACTION (RAYCASTING)
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    window.addEventListener('pointerdown', (event) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const meshes = cubes.map(c => c.mesh);
      const intersects = raycaster.intersectObjects(meshes);

      if (intersects.length > 0) {
        // Direct click on a cube: unfreeze initial state if needed, then split
        const hitMesh = intersects[0].object;
        const index = cubes.findIndex(c => c.mesh === hitMesh);

        if (cubes[index].isInitial) {
          cubes[index].body.mass = cubes[index].size * 2;
          cubes[index].body.updateMassProperties();
          cubes[index].isInitial = false;
        }

        splitCube(index);
      } else {
        // Click on background: teleport all active cubes to click position and drop
        const target3D = new THREE.Vector3();
        raycaster.ray.at(14, target3D); // Project hit point in front of camera

        cubes.forEach(c => {
          if (c.isInitial) {
            c.body.mass = c.size * 2;
            c.body.updateMassProperties();
            c.isInitial = false;
          }

          c.body.position.set(
            target3D.x + (Math.random() - 0.5) * 2,
            target3D.y + (Math.random() - 0.5) * 2,
            target3D.z + (Math.random() - 0.5) * 2
          );

          // Reset velocity and give vertical drop momentum
          c.body.velocity.set(
            (Math.random() - 0.5) * 2,
            2,
            (Math.random() - 0.5) * 2
          );
        });
      }
    });

    // 6. ANIMATION LOOP
    const clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);

      const delta = clock.getDelta();
      world.step(1 / 60, delta, 3);

      // Sync visual mesh positions to rigid body positions
      cubes.forEach(c => {
        c.mesh.position.copy(c.body.position);
        c.mesh.quaternion.copy(c.body.quaternion);
      });

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
"""

# Render the game inside Streamlit
components.html(game_html, height=620, scrolling=False)
