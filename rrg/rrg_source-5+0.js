for(var i=scene.lights.count-1; i >= 0; i--)
  scene.lights.removeByIndex(i);

L0=scene.createLight();
L0.direction.set(-0.577350269189626,-0.577350269189626,-0.577350269189626);
L0.color.set(1,1,1);

scene.lightScheme=scene.LIGHT_MODE_HEADLAMP;
scene.lightScheme=scene.LIGHT_MODE_FILE;
