module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace']
      },
      colors: {
        night: '#0c0d12',
        ink: '#171923',
        haze: '#cbd5f5',
        neon: '#5bf7b1',
        ember: '#ff7f50',
        steel: '#8ba3c7'
      },
      boxShadow: {
        glow: '0 0 40px rgba(91, 247, 177, 0.2)'
      }
    }
  },
  plugins: []
};
