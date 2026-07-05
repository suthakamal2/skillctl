#!/usr/bin/env node
/** MIT-licensed */
const { spawnSync } = require('child_process');

function run() {
  const args = process.argv.slice(2);
  
  // Check if skillctl is in PATH
  let result = spawnSync('skillctl', args, { stdio: 'inherit' });
  
  if (result.error && result.error.code === 'ENOENT') {
    console.log("skillctl not found on PATH. Installing via pip...");
    const installResult = spawnSync('python3', ['-m', 'pip', 'install', '--user', 'skillctl'], { stdio: 'inherit' });
    if (installResult.status !== 0) {
      console.error("Failed to install skillctl via pip.");
      process.exit(installResult.status || 1);
    }
    
    // Re-execute after install
    result = spawnSync('skillctl', args, { stdio: 'inherit' });
  }
  
  if (result.error) {
    console.error("Failed to execute skillctl:", result.error.message);
    process.exit(1);
  }
  
  process.exit(result.status);
}

run();
