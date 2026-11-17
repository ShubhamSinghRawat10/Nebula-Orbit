/* Nebula's lightweight, vanilla-canvas interpretation of React Bits Ghost Fibers. */
(() => {
  const canvas = document.querySelector("#ghost-fibers-background");
  const context = canvas?.getContext("2d", { alpha: true });
  if (!canvas || !context) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const fibers = [];
  const colors = [
    { core: "191, 164, 255", glow: "116, 91, 255" },
    { core: "133, 174, 255", glow: "61, 114, 255" },
    { core: "214, 224, 255", glow: "112, 146, 255" },
  ];
  let width = 0;
  let height = 0;
  let pixelRatio = 1;
  let frame = 0;
  let previousFrame = 0;

  // Keep the denser ribbons toward the right and lower edges, clear of reading areas.
  const bundles = [
    { x: 0.57, spread: 86, amplitude: 37, phase: 0.2, speed: 0.00012, color: 0 },
    { x: 0.78, spread: 112, amplitude: 52, phase: 2.1, speed: 0.00016, color: 1 },
    { x: 0.97, spread: 70, amplitude: 32, phase: 4.4, speed: 0.0001, color: 2 },
  ];

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.round(width * pixelRatio);
    canvas.height = Math.round(height * pixelRatio);
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    draw(performance.now());
  }

  function draw(now) {
    context.clearRect(0, 0, width, height);
    context.globalCompositeOperation = "lighter";
    const compact = width < 720;

    bundles.forEach((bundle, bundleIndex) => {
      const color = colors[bundle.color];
      const count = compact ? 16 : 27;
      const spread = compact ? bundle.spread * 0.52 : bundle.spread;
      const amplitude = compact ? bundle.amplitude * 0.62 : bundle.amplitude;
      const centerX = width * bundle.x;
      const phase = reducedMotion.matches ? bundle.phase : bundle.phase + now * bundle.speed;

      for (let index = 0; index < count; index += 1) {
        const offset = (index / Math.max(1, count - 1) - 0.5) * spread;
        const strandPhase = phase + index * 0.075 + bundleIndex * 0.6;
        const visibility = 0.3 + 0.7 * Math.sin((index / count) * Math.PI);

        context.beginPath();
        for (let step = 0; step <= 44; step += 1) {
          const progress = step / 44;
          const y = progress * (height + 160) - 80;
          const broadWave = Math.sin(progress * 5.8 + strandPhase) * amplitude;
          const fineWave = Math.sin(progress * 13.4 - strandPhase * 1.7) * 8;
          const x = centerX + offset + broadWave + fineWave;
          if (step === 0) context.moveTo(x, y);
          else context.lineTo(x, y);
        }

        context.lineWidth = 5;
        context.strokeStyle = `rgba(${color.glow}, ${0.012 * visibility})`;
        context.shadowBlur = 18;
        context.shadowColor = `rgba(${color.glow}, 0.12)`;
        context.stroke();

        context.lineWidth = 0.8;
        context.strokeStyle = `rgba(${color.core}, ${0.13 * visibility})`;
        context.shadowBlur = 4;
        context.shadowColor = `rgba(${color.core}, 0.2)`;
        context.stroke();
      }
    });

    context.globalCompositeOperation = "source-over";
    context.shadowBlur = 0;
  }

  function animate(now) {
    frame = 0;
    if (document.hidden) return;
    if (!reducedMotion.matches && now - previousFrame >= 34) {
      draw(now);
      previousFrame = now;
    }
    if (!reducedMotion.matches) frame = window.requestAnimationFrame(animate);
  }

  function start() {
    if (!reducedMotion.matches && !document.hidden && !frame) {
      frame = window.requestAnimationFrame(animate);
    }
  }

  function stop() {
    if (frame) window.cancelAnimationFrame(frame);
    frame = 0;
  }

  window.addEventListener("resize", resize, { passive: true });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop();
    else start();
  });
  reducedMotion.addEventListener?.("change", () => {
    stop();
    draw(performance.now());
    start();
  });

  resize();
  start();
})();
