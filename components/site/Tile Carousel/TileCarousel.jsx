import React, { useEffect, useRef } from 'react';

export function TileCarousel() {
  const containerRef = useRef(null);

  useEffect(() => {
    const u = (min) => Math.min(window.innerWidth / 1440, window.innerHeight / 1080) * min;
    const cardCount = 10;
    const cardPitch = u(196);
    const scrollSpeed = u(25); // Gentle auto-scroll speed

    let currentX = 0;
    let lastTime = Date.now();
    let animationFrameId;

    const carousel = containerRef.current;
    if (!carousel) return;

    // Array of your exact salt and spice video sources
    const videoSources = [
      'https://assets.mixkit.co/videos/preview/mixkit-close-up-of-grains-of-salt-in-a-bowl-43093-large.mp4', // Salt crystals
      'https://assets.mixkit.co/videos/preview/mixkit-spices-in-bowls-on-a-table-42352-large.mp4' // Spices assortment
    ];

    carousel.innerHTML = '';
    const cards = [];

    const gridPositions = [
      { x: 0, y: 0 }, { x: 384, y: 0 }, { x: 768, y: 0 }, { x: 1152, y: 0 }, { x: 1536, y: 0 },
      { x: 0, y: 540 }, { x: 384, y: 540 }, { x: 768, y: 540 }, { x: 1152, y: 540 }, { x: 1536, y: 540 }
    ];

    for (let i = 0; i < cardCount; i++) {
      const card = document.createElement('div');
      card.className = 'relative flex-shrink-0 w-48 h-72 rounded-2xl overflow-hidden border border-stone-800 bg-stone-900 shadow-xl transition-all duration-300 hover:border-amber-500/50';

      const video = document.createElement('video');
      // Alternate between your salt and spice videos across the 10 tiles
      video.src = videoSources[i % videoSources.length];
      video.muted = true;
      video.loop = true;
      video.playsInline = true;
      video.autoplay = true;

      const pos = gridPositions[i % gridPositions.length];
      video.style.objectFit = 'cover';
      video.style.objectPosition = `-${pos.x}px -${pos.y}px`;
      video.style.width = '500%';
      video.style.height = '140%';

      card.appendChild(video);
      carousel.appendChild(card);
      cards.push({ element: card, video, index: i });

      video.play().catch(() => {});
    }

    function animate() {
      const now = Date.now();
      const deltaTime = (now - lastTime) / 1000;
      lastTime = now;

      currentX -= scrollSpeed * deltaTime;

      cards.forEach((card) => {
        const totalWidth = cardCount * cardPitch;
        const itemOffset = card.index * cardPitch;
        let cardX = (currentX + itemOffset) % totalWidth;
        if (cardX < -cardPitch / 2) cardX += totalWidth;

        card.element.style.transform = `translateX(${cardX}px)`;
      });

      animationFrameId = requestAnimationFrame(animate);
    }

    animationFrameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <section className="py-24 bg-stone-950 overflow-hidden border-t border-stone-900">
      <div className="max-w-7xl mx-auto px-6 mb-12">
        <span className="text-xs font-mono uppercase tracking-widest text-amber-500">Gallery</span>
        <h2 className="text-3xl md:text-5xl font-serif text-stone-100 mt-2">The seam, the mill, the load.</h2>
        <p className="text-stone-400 mt-2 text-sm">Explore our pink salt extraction workflow, milling lines, and port logistics stream.</p>
      </div>

      {/* Carousel Container */}
      <div
        ref={containerRef}
        className="relative flex items-center h-80 w-full overflow-hidden cursor-grab active:cursor-grabbing px-6 select-none"
      />
    </section>
  );
}
