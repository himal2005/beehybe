import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Cube Splitter Games", layout="wide")

st.title("🎲 Cube Splitter Physics Games")

# Create tabs to select between 3D Click-to-Split and 2D Ground-Split games
tab1, tab2 = st.tabs(["3D Click-to-Split Game", "2D Ground-Split Game"])

# ==========================================
# TAB 1: 3D CLICK-TO-SPLIT GAME
# ==========================================
with tab1:
    st.write("Click a cube directly to drop and split it in 3D space. Click elsewhere on the background to gather all cubes to your cursor.")
    
    game_3d_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        body { margin: 0; overflow: hidden; background-color: #141419; font-family: sans-serif; }
        #canvas-container-3d { width: 100vw; height: 600px; position: relative; }
        #counter-3d {
          position: absolute;
          top: 15px;
          left: 15px;
          background: rgba(0, 0, 0, 0.7);
          color: #00ffcc;
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 18px;
          font-weight: bold;
          border: 1px solid #00ffcc;
          pointer-events: none;
          z-index: 10;
        }
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"></script>
    </head>
    <body>
      <div id="canvas-container-3d">
        <div id="counter-3d">Cube Count: 1</div>
      </div>

      <script>
        const container = document.getElementById('canvas-container-3d');
        const counterEl = document.getElementById('counter-3d');

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x141419);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 600, 0.1, 1000);
        camera.position.set(0, 5, 18);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, 600);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 10);
        dirLight.castShadow = true;
        scene.add(dirLight);

        const world = new CANNON.World();
        world.gravity.set(0, -20, 0);

        const bouncyMaterial = new CANNON.Material('bouncy');
        const contactMaterial = new CANNON.ContactMaterial(bouncyMaterial, bouncyMaterial, {
          friction: 0.2, restitution: 0.8
        });
        world.addContactMaterial(contactMaterial);

        const groundBody = new CANNON.Body({ mass: 0, shape: new CANNON.Plane(), material: bouncyMaterial });
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

        const cubes = [];

        function updateCounter() {
          counterEl.innerText = 'Cube Count: ' + cubes.length;
        }

        function createCube(position, size, isInitial = false) {
          const color = new THREE.Color().setHSL(Math.random(), 0.85, 0.55);
          const geometry = new THREE.BoxGeometry(size, size, size);
          const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.3 });
          const mesh = new THREE.Mesh(geometry, material);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          scene.add(mesh);

          const shape = new CANNON.Box(new CANNON.Vec3(size / 2, size / 2, size / 2));
          const body = new CANNON.Body({ mass: isInitial ? 0 : size * 2, shape: shape, material: bouncyMaterial });
          body.position.copy(position);
          world.addBody(body);

          const cubeObj = { mesh, body, size, isInitial };
          cubes.push(cubeObj);
          updateCounter();
          return cubeObj;
        }

        createCube(new CANNON.Vec3(0, 2, 0), 3, true);

        function splitCube(cubeIndex) {
          const parent = cubes[cubeIndex];
          scene.remove(parent.mesh);
          world.remove(parent.body);
          cubes.splice(cubeIndex, 1);

          const newSize = parent.size * 0.75;
          if (newSize < 0.25) { updateCounter(); return; }

          for (let i = 0; i < 2; i++) {
            const offset = (i === 0 ? -1 : 1) * (newSize / 2);
            const childPos = new CANNON.Vec3(parent.body.position.x + offset, parent.body.position.y + 0.2, parent.body.position.z);
            const child = createCube(childPos, newSize, false);
            child.body.velocity.set((Math.random() - 0.5) * 6 + (i === 0 ? -3 : 3), Math.random() * 5 + 3, (Math.random() - 0.5) * 6);
          }
        }

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('pointerdown', (event) => {
          const rect = renderer.domElement.getBoundingClientRect();
          mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

          raycaster.setFromCamera(mouse, camera);
          const intersects = raycaster.intersectObjects(cubes.map(c => c.mesh));

          if (intersects.length > 0) {
            const hitMesh = intersects[0].object;
            const index = cubes.findIndex(c => c.mesh === hitMesh);
            if (cubes[index].isInitial) {
              cubes[index].body.mass = cubes[index].size * 2;
              cubes[index].body.updateMassProperties();
              cubes[index].isInitial = false;
            }
            splitCube(index);
          } else {
            const target3D = new THREE.Vector3();
            raycaster.ray.at(14, target3D);
            cubes.forEach(c => {
              if (c.isInitial) {
                c.body.mass = c.size * 2;
                c.body.updateMassProperties();
                c.isInitial = false;
              }
              c.body.position.set(target3D.x + (Math.random() - 0.5) * 2, target3D.y + (Math.random() - 0.5) * 2, target3D.z + (Math.random() - 0.5) * 2);
              c.body.velocity.set((Math.random() - 0.5) * 2, 2, (Math.random() - 0.5) * 2);
            });
          }
        });

        const clock = new THREE.Clock();
        function animate() {
          requestAnimationFrame(animate);
          world.step(1 / 60, clock.getDelta(), 3);
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
    components.html(game_3d_html, height=620, scrolling=False)

# ==========================================
# TAB 2: 2D GROUND-SPLIT GAME
# ==========================================
with tab2:
    st.write("Click anywhere to drop/gather cubes. Every cube automatically **splits into two when hitting the ground**!")

    game_2d_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        body { margin: 0; overflow: hidden; background-color: #1a1a24; font-family: sans-serif; }
        #canvas-container-2d { width: 100vw; height: 600px; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background-color: #0f0f17; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); }
        #counter-2d {
          position: absolute;
          top: 15px;
          left: 15px;
          background: rgba(0, 0, 0, 0.7);
          color: #ff0077;
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 18px;
          font-weight: bold;
          border: 1px solid #ff0077;
          pointer-events: none;
          z-index: 10;
        }
      </style>
    </head>
    <body>
      <div id="canvas-container-2d">
        <div id="counter-2d">Cube Count: 1</div>
        <canvas id="gameCanvas" width="900" height="600"></canvas>
      </div>

      <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const counterEl = document.getElementById('counter-2d');

        const GRAVITY = 0.45;
        const BOUNCE = -0.75;
        const GROUND_Y = canvas.height - 40;
        const MIN_SIZE = 8;

        let cubes = [];

        class Cube {
          constructor(x, y, size, vx = 0, vy = 0, isInitial = false) {
            this.x = x;
            this.y = y;
            this.size = size;
            this.vx = vx;
            this.vy = vy;
            this.isInitial = isInitial;
            this.color = `hsl(${Math.random() * 360}, 80%, 60%)`;
            this.hasSplit = false;
          }

          update() {
            if (this.isInitial) return;
            this.vy += GRAVITY;
            this.x += this.vx;
            this.y += this.vy;
            this.vx *= 0.99;

            if (this.x - this.size / 2 < 0) {
              this.x = this.size / 2;
              this.vx *= -1;
            } else if (this.x + this.size / 2 > canvas.width) {
              this.x = canvas.width - this.size / 2;
              this.vx *= -1;
            }

            if (this.y + this.size / 2 >= GROUND_Y) {
              this.y = GROUND_Y - this.size / 2;
              this.vy *= BOUNCE;
              this.hasSplit = true;
            }
          }

          draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.fillStyle = this.color;
            ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(-this.size / 2, -this.size / 2, this.size, this.size);
            ctx.restore();
          }
        }

        function resetGame() {
          cubes = [new Cube(canvas.width / 2, 150, 60, 0, 0, true)];
          counterEl.innerText = 'Cube Count: 1';
        }

        function handleGroundSplits() {
          const nextCubes = [];
          cubes.forEach(cube => {
            if (cube.hasSplit && cube.size > MIN_SIZE) {
              const newSize = cube.size * 0.7;
              const c1 = new Cube(cube.x - newSize / 3, cube.y - 5, newSize, -Math.random() * 4 - 2, cube.vy * 0.9);
              const c2 = new Cube(cube.x + newSize / 3, cube.y - 5, newSize, Math.random() * 4 + 2, cube.vy * 0.9);
              nextCubes.push(c1, c2);
            } else {
              cube.hasSplit = false;
              nextCubes.push(cube);
            }
          });
          cubes = nextCubes;
          counterEl.innerText = 'Cube Count: ' + cubes.length;
        }

        canvas.addEventListener('pointerdown', (event) => {
          const rect = canvas.getBoundingClientRect();
          const clickX = event.clientX - rect.left;
          const clickY = event.clientY - rect.top;

          cubes.forEach(cube => {
            if (cube.isInitial) cube.isInitial = false;
            cube.x = clickX + (Math.random() - 0.5) * 20;
            cube.y = clickY + (Math.random() - 0.5) * 20;
            cube.vx = (Math.random() - 0.5) * 6;
            cube.vy = -Math.random() * 3;
            cube.hasSplit = false;
          });
        });

        function gameLoop() {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = '#22223b';
          ctx.fillRect(0, GROUND_Y, canvas.width, canvas.height - GROUND_Y);
          ctx.strokeStyle = '#4a4e69';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(0, GROUND_Y);
          ctx.lineTo(canvas.width, GROUND_Y);
          ctx.stroke();

          cubes.forEach(cube => cube.update());
          handleGroundSplits();
          cubes.forEach(cube => cube.draw());

          requestAnimationFrame(gameLoop);
        }

        resetGame();
        gameLoop();
      </script>
    </body>
    </html>
    """
    components.html(game_2d_html, height=620, scrolling=False)

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
